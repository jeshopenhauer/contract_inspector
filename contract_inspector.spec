# contract_inspector.spec
# Archivo de configuración para PyInstaller

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('index.html', '.'),
        ('style.css', '.'),
        ('functions.js', '.'),
        ('inspector_functions/*', 'inspector_functions'),
        ('template/*', 'template'),
        # Asegurarse de que la carpeta output_split existe en el ejecutable
        ('output_split', 'output_split'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'pdfminer',
        'pdfminer.high_level',
        'pdfminer.layout',
        'webbrowser',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ContractInspector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ContractInspector'
)