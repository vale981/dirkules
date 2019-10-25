from dirkules.models import Pool

from dirkules.config import staticDir

from dirkules import db, app_version, app

from dirkules.samba.models import SambaGlobal, SambaShare, SambaOption


def get_pools():
    pools = Pool.query.all()
    choices = [(pool.id, pool.label) for pool in pools]
    return choices


def create_share(name, path, user, dir_mask, create_mask, writeable, btrfs, recycling):
    """
    Creates a samba share in db with all needed options for proper generation.
    :param name: Share name
    :type name: String
    :param path: Path to share. might change in later versions.
    :type path: String
    :param user: User which is allowed to access
    :type user: String
    :param dir_mask: The UNIX octal mask for directories in share
    :type dir_mask: Integer
    :param create_mask: The UNIX octal mask for files in share
    :type create_mask: Integer
    :param writeable: Defines whether share is writeable or not
    :type writeable: Boolean
    :param btrfs: Defines the btrfs vfs_object
    :type btrfs: Boolean
    :param recycling: Defines the recycle vfs_object
    :type recycling: Boolean
    :return: Nothing
    :rtype: None
    """
    share = SambaShare(name, path, btrfs=btrfs, recycle=recycling)
    user = SambaOption("valid users", user)
    if dir_mask is None:
        dir_mask = "0700"
    if create_mask is None:
        create_mask = "0600"
    dir_mask = SambaOption("directory mask", dir_mask)
    create_mask = SambaOption("create mask", create_mask)
    if writeable:
        writeable = SambaOption("writeable", "yes")
    else:
        writeable = SambaOption("writeable", "no")
    share.options.extend([user, dir_mask, create_mask, writeable])
    db.session.add(share)
    db.session.commit()


def set_samba_global(workgroup, name):
    """
    Sets the variables for the [global] part in smb.conf
    :param workgroup: Workgroup name
    :type workgroup: string
    :param name: Smbd server name
    :type name: string
    :return: nothing
    :rtype: None
    """
    SambaGlobal.query.delete()
    workgroup = SambaGlobal("workgroup", workgroup)
    name = SambaGlobal("server string", "%h {}".format(name))
    db.session.add(workgroup)
    db.session.add(name)
    db.session.commit()


def generate_smb():
    """
    Function is used to generate a new smb.conf file
    :return: nothing
    :rtype: None
    """
    if SambaGlobal.query.first() is None:
        app.logger.warning("Samba not configured. Using default fallback.")
        workgroup = 'WORKGROUP'
        server_string = '%h dirkules'
    else:
        workgroup = SambaGlobal.query.get(1)
        server_string = SambaGlobal.query.get(2)
    f = open("smb.conf.txt", "w")
    samba_global = open(staticDir + "/conf/samba_global.conf", "r")
    f.write("# This file was generated by dirkules v{}\n".format(app_version))
    f.write("")
    f.write("# Global Config\n")
    f.write("server string = {}\n".format(server_string))
    f.write("workgroup = {}\n".format(workgroup))
    f.write(samba_global.read())
    f.close()
    app.logger.info("Generated new samba config.")
