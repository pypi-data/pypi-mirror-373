from typing import Any

import os
import glob
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from ut_log.log import Log, LogEq
from ut_dic.dic import Dic
from ut_path.pathnm import PathNm
from ut_path.path import Path
from ut_path.path import AoPath
from ut_ctl.journalctl import Journalctl

TyArr = list[Any]
TyDic = dict[Any, Any]
TyStr = str
TyPath = str
TyAoPath = list[str]

TnPath = None | TyPath


class PmeHandler(PatternMatchingEventHandler):
    """
    WatchDog Event Handler for pattern matching of files paths
    """
    msg_evt: TyStr = "Watchdog received {E} - {P}"
    msg_exe: TyStr = "Watchdog executes script: {S}"

    def __init__(self, patterns, scripts):
        # Set the patterns for PatternMatchingEventHandler
        # self.kwargs = kwargs
        super().__init__(
                patterns=patterns,
                ignore_patterns=None,
                ignore_directories=True,
                case_sensitive=False)
        self.scripts = scripts

    def ex(self):
        """
        Process created or modified event
        """
        Log.debug(f"Watchdog executes scripts: {self.scripts}")
        for _script in self.scripts:
            Log.debug(f"Watchdog executes script: {_script}")
            if os.path.exists(_script):
                os.system(_script)
            else:
                Log.error(f"Script {_script} not found")

    def on_created(self, event):
        """
        Process 'files paths are created' event
        """
        _path = event.src_path
        Log.debug(f"Watchdog received created event = {event} for path = {_path}")
        self.ex()

    def on_modified(self, event):
        """
        Process 'files paths are modified' event
        """
        _path = event.src_path
        Log.debug(f"Watchdog received modified event = {event} for path = {_path}")
        self.ex()


class WdP:
    """
    Watch Dog Processor
    """
    @staticmethod
    def sh_scripts(kwargs: TyDic) -> TyArr:
        """
        WatchDog Task for pattern matching of files paths
        """
        _scripts: TyArr = Dic.get_as_array(kwargs, 'scripts')
        LogEq.debug("_scripts", _scripts)

        _scripts_new = []
        for _script in _scripts:
            LogEq.debug("_script", _script)
            _script = Path.sh_path_by_tpl_pac_sep(_script, kwargs)
            LogEq.debug("_script", _script)
            _scripts_new.append(_script)
        LogEq.debug("_scripts_new", _scripts_new)
        return _scripts_new

    @classmethod
    def sh_a_path_gt_threshold(
            cls, in_dir, in_patterns, kwargs: TyDic) -> TyAoPath:
        """
        WatchDog Task for pattern matching of files paths
        """
        _a_path: TyAoPath = []
        _service_name = kwargs.get('service_name', '')
        # _last_stop_ts = Journalctl.get_last_stop_ts_s(_service_name)
        _last_stop_ts = Journalctl.get_last_stop_ts_s(_service_name)
        Log.debug(f"_last_stop_ts: {_last_stop_ts} for service: {_service_name}")
        if not _last_stop_ts:
            return _a_path

        for _path in in_patterns:
            _path_new = os.path.join(in_dir, _path)
            _a_path = _a_path + glob.glob(_path_new)
        msg = f"_a_path: {_a_path} for in_dir: {in_dir}, _in_patterns: {in_patterns}"
        Log.debug(msg)
        _a_path = AoPath.sh_aopath_mtime_gt_threshold(_a_path, _last_stop_ts)
        Log.debug(f"_a_path: {_a_path} after selection by threshhold: {_last_stop_ts}")
        return _a_path

    @classmethod
    def pmeh(cls, kwargs: TyDic) -> None:
        """
        WatchDog Task for pattern matching of files paths
        """
        _in_dir = PathNm.sh_path('in_dir', kwargs)
        _in_patterns: TyArr = Dic.get_as_array(kwargs, 'in_patterns')
        _scripts: TyArr = cls.sh_scripts(kwargs)

        LogEq.debug("_in_dir", _in_dir)
        LogEq.debug("_in_patterns", _in_patterns)
        LogEq.debug("_scripts", _scripts)

        _pmehandler = PmeHandler(_in_patterns, _scripts)

        _sw_ex_gt_threshold = kwargs.get('sw_ex_gt_threshold', False)
        if _sw_ex_gt_threshold:
            _a_path = cls.sh_a_path_gt_threshold(_in_dir, _in_patterns, kwargs)
            if len(_a_path) > 0:
                _pmehandler.ex()

        _observer = Observer()
        _observer.schedule(_pmehandler, path=_in_dir, recursive=False)
        _observer.start()

        _sleep: int = kwargs.get('sleep', 1)
        try:
            while True:
                time.sleep(_sleep)
        except KeyboardInterrupt:
            _observer.stop()
        _observer.join()
