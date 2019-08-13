from dirkules import db
from dirkules.models import Drive, Partitions, Pool
from dirkules.hardware import drive as hardware_drives
from sqlalchemy.sql.expression import exists, and_
import dirkules.hardware.btrfsTools as btrfsTools
import dirkules.hardware.ext4Tools as ext4Tools


# get partitions from hardware (method) and store in db
# contains all logic like replacing, removing in future
def get_partitions(drive_id, force=False):
    drive = db.session.query(Drive).get(drive_id)
    partdict = hardware_drives.part_for_disk(drive.name)
    for part in partdict:
        existence = db.session.query(
            exists().where(and_(Partitions.uuid == part.get("uuid"), Partitions.name == part.get("name")))).scalar()
        if not existence:
            if part.get("label") == "":
                label = "none"
            else:
                label = part.get("label")
            part_obj = Partitions(drive.id, part.get("name"), label, part.get("fs"), int(part.get("size")),
                                  part.get("uuid"), part.get("mount"), drive)
            print(part.get("name") + " NICHT in db")
            db.session.add(part_obj)
            db.session.commit()


def pool_gen():
    part_dict = dict()
    # creates map uuid is key, partitions are values
    for part in Partitions.query.all():
        if part.uuid in part_dict:
            part_dict[part.uuid].append(part)
        else:
            part_dict.update({part.uuid: [part]})

    for key, value in part_dict.items():
        if len(value) == 1:
            raid = "Single"
        else:
            raid = "unknown RAID"
        drives = ""
        for part in value:
            drives = drives + str(Drive.query.get(part.drive_id)) + ","
        drives = drives[:-1]
        value = value[0]
        existence = db.session.query(exists().where(and_(Pool.drives == drives, Pool.fs == value.fs))).scalar()
        # FS is ext4 or BtrFS and there is no element in db with such a part constellation
        # TODO: Warning: If a partition has been added to a raid, the disk will still exist
        # because not removed and the pool will be displayed twice, because not same part constellation
        if value.fs == "btrfs" and not existence:
            memory_map = btrfsTools.get_space(value.mountpoint)
            pool_obj = Pool(value.label, memory_map.get("total"), memory_map.get("free"), raid, value.fs,
                            value.mountpoint,
                            "not implemented", drives)
            db.session.add(pool_obj)
            db.session.commit()

        if value.fs == "ext4" and not existence:
            if value.mountpoint:
                free_space = ext4Tools.get_free_space(value.name)
            else:
                free_space = 2
            pool_obj = Pool(value.label, value.size, free_space, raid, value.fs,
                            value.mountpoint,
                            "not implemented", drives)
            db.session.add(pool_obj)
            db.session.commit()
