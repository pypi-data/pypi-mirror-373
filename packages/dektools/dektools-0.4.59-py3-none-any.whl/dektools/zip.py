import os
import tempfile
import zipfile
import shutil
from io import BytesIO
from zipfile import ZipFile, ZipInfo
from .file import remove_path, sure_dir, sure_read, normal_path, clear_dir, sure_parent_dir


class ZipFilePlus(ZipFile):
    # https://stackoverflow.com/a/46837272/15543185
    ZIP_UNIX_SYSTEM = 3

    def _extract_member(self, member, targetpath, pwd):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = member.filename.replace('/', os.path.sep)

        if os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname as relative, remove drive letter or
        # UNC path, redundant separators, "." and ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        invalid_path_parts = ('', os.path.curdir, os.path.pardir)
        arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                                   if x not in invalid_path_parts)
        if os.path.sep == '\\':
            # filter illegal characters on Windows
            arcname = self._sanitize_windows_name(arcname, os.path.sep)

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if member.is_dir():
            if not os.path.isdir(targetpath):
                os.mkdir(targetpath)
            return targetpath

        with self.open(member, pwd=pwd) as source, \
                open(targetpath, "wb") as target:
            shutil.copyfileobj(source, target)

        self.set_member_attributes(targetpath, member)

        return targetpath

    @classmethod
    def set_member_attributes(cls, path, member):
        if member.create_system == cls.ZIP_UNIX_SYSTEM:
            unix_attributes = member.external_attr >> 16
            if unix_attributes:
                os.chmod(path, unix_attributes)


def compress_files(
        src, path_zip=None, path_set=None, combine=False, prefix=None,
        compression=zipfile.ZIP_BZIP2,
        allowZip64=True,
        compresslevel=9,
        **kwargs):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    src = normal_path(src)
    if path_zip is None:
        zip_file = BytesIO()
    else:
        path_zip = normal_path(path_zip)
        sure_parent_dir(path_zip)
        if not combine:
            remove_path(path_zip)
        zip_file = path_zip
    with zipfile.ZipFile(
            zip_file, mode='w',
            compression=compression,
            allowZip64=allowZip64,
            compresslevel=compresslevel,
            **kwargs
    ) as zf:
        if os.path.isfile(src):
            pp = os.path.basename(src)
            if prefix:
                pp = f"{prefix}/{pp}"
            zf.write(src, pp)
        else:
            if path_set is None:
                need_normal = os.sep == '/'
                for base, _, files in os.walk(src):
                    for file in files:
                        p = os.path.join(base, file)
                        pp = p[len(src):]
                        if prefix:
                            pp = f"{prefix}/{pp}"
                        if need_normal and os.path.islink(p):
                            p = os.path.realpath(p).replace('\\', '/')
                        try:
                            zf.write(p, pp)
                        except FileNotFoundError:
                            pass
            else:
                for p in path_set:
                    p = normal_path(p)
                    if not p.startswith(src + os.path.sep):
                        raise ValueError(f'[{p}] not child of [{src}]')
                    pp = p[len(src):]
                    if prefix:
                        pp = f"{prefix}/{pp}"
                    zf.write(os.path.normpath(os.path.realpath(p)), pp)
    return zip_file.getvalue() if path_zip is None else zip_file


def decompress_files(zip_file, dest_dir=None, combine=False):
    if not dest_dir:
        dest_dir = tempfile.mkdtemp()
    dest_dir = normal_path(dest_dir)
    sure_dir(dest_dir)
    if not combine:
        clear_dir(dest_dir)
    try:
        with ZipFilePlus(sure_read(zip_file)) as zip_ref:
            zip_ref.extractall(dest_dir)
    except zipfile.BadZipfile:
        shutil.unpack_archive(zip_file, dest_dir)
    return dest_dir


def take_bytes(zip_file, path_in_zip):  # path_in_zip is a relative path in zip file
    with zipfile.ZipFile(sure_read(zip_file)) as zip_ref:
        try:
            return zip_ref.read(path_in_zip)
        except KeyError:
            return None


def take_file(zip_file, path_in_zip, path_out):
    path_out = normal_path(path_out)
    sure_parent_dir(path_out)
    with ZipFilePlus(sure_read(zip_file)) as zip_ref:
        try:
            with zip_ref.open(path_in_zip) as zf, open(path_out, 'wb') as f:
                shutil.copyfileobj(zf, f)
                member = zip_ref.getinfo(zf.name)
            zip_ref.set_member_attributes(path_out, member)
            return True
        except KeyError:
            return False
