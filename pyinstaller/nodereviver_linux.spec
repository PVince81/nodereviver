# -*- mode: python -*-
projectpath = '/home/vincent/workspace/minild33/'
pyinstallerpath = '/home/vincent/progs/pyinstaller'
datapath = projectpath + "data/"
a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), projectpath + 'nodereviver.py'],
             pathex=[pyinstallerpath])
pyz = PYZ(a.pure)
a.binaries = [x for x in a.binaries if not 
              (os.path.basename(x[1]).lower() in ("msvcr90.dll", "msvcm90.dll", "kernel32.dll", "msvcp90.dll") or ("microsoft" in x[1].lower()))]
		  
pyd = []
other = []
for binary in a.binaries:
	if os.path.splitext(binary[1])[1].lower() == ".pyd":
		pyd.append(binary)
	else:
		other.append(binary)

for file in os.listdir(datapath):
	a.datas.append(("data/" + os.path.basename(file), datapath + file, 'DATA'))

a.datas.append(("README.txt", projectpath + "README.txt", "DATA"))	

exe = EXE( pyz,
          a.scripts,
          a.zipfiles,
		  pyd,
          name=os.path.join('dist', 'nodereviver_run'),
          debug=False,
          strip=False,
          upx=True,
          console=False , icon=projectpath + 'misc/nodereviver.ico')
	  
coll = COLLECT( exe,
				a.datas,
               other,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'nodereviver'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'nodereviver.app'))
