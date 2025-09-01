import stat
import os
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager
from jupyter_server.utils import to_os_path, ApiPath

LUCIEN_NOTEBOOK_DIR = "lucien-notebook"

class PathResolverKernelManager(AsyncMappingKernelManager):

    def cwd_for_path(self, path: ApiPath, **kwargs):
        os_path = to_os_path(path, self.root_dir)
        # 当前os_path是notebook文件所在的目录
        while not os.path.isdir(os_path) and os_path != self.root_dir:
            os_path = os.path.dirname(os_path)

        if path.startswith(LUCIEN_NOTEBOOK_DIR):
            # 判断是否是软链/junction
            os_path_dir = to_os_path(ApiPath(LUCIEN_NOTEBOOK_DIR), self.root_dir)
            lstat = os.lstat(os_path_dir)
            if stat.S_ISLNK(lstat.st_mode):
                return self.root_dir

            if stat.S_ISDIR(lstat.st_mode) and os.path.isjunction(os_path_dir):
                return self.root_dir

        # 非 lucien-notebook 目录, 返回默认的路径
        return os_path
