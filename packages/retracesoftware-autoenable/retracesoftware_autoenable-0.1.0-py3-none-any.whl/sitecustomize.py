import os

if 'RETRACE_MODE' in os.environ:
    try:
        from retracesoftware.install.patcher import install
        install(os.environ['RETRACE_MODE'].lower())

    except Exception as error:
        print(f"❌ Caught exception: {error}")
        import traceback
        traceback.print_exc()
        os._exit(1)

