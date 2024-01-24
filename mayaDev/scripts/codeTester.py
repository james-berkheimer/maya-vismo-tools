import os.path
import os, shutil, glob
import time
import re
import sys, string
import subprocess

launchDeadline = ['C:\\Program Files\\Thinkbox\\Deadline10\\bin\\deadlinecommandbg.exe', '-executescript', '\\\\RenderFarm10\\DeadlineRepository10\\custom\\scripts\\Submission\\Modo\\VISMO_ModoSubmission_D10.py', 'O:\\Clients\\Lilly\\Lasmiditan\\LILLA_MOD_18_5242\\Animation\\LILLA_MODO\\_DVLP\\mm\\LILLA_dvlp00_v014_MM.lxo', '1-600', 1211, 'LILLA', '_DVLP', '1280x720', 'PNG', '', 'O:\\Clients\\Lilly\\Lasmiditan\\LILLA_MOD_18_5242\\Animation\\frames\\MODO_LILLA__DVLP\\mm\\LILLA_dvlp00_v014\\COL\\Global_col\\LILLA_dvlp00_v014_Global_col_,PNG', 'v015', 'O:\\Clients\\Lilly\\Lasmiditan\\LILLA_MOD_18_5242\\Animation']

process = subprocess.Popen(launchDeadline, stdout=subprocess.PIPE)
