import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les.eject_pilot_level_actor()
les.editor_set_game_view(True)
ues.set_level_viewport_camera_info(LOC, ROT)
unreal.SystemLibrary.execute_console_command(None, f"HighResShot {W}x{H} filename={OUT}")
