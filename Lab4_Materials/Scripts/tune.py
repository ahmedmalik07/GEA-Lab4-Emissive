import unreal
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
def mi(n): return unreal.load_asset("/Game/Lab4/" + n)
for n in ("MI_Prop_Clean", "MI_Prop_Worn"):
    m = mi(n); mel.set_material_instance_static_switch_parameter_value(m, "Enable_Emissive", False)
    mel.update_material_instance(m); eal.save_loaded_asset(m)
m = mi("MI_Emissive_On"); mel.set_material_instance_scalar_parameter_value(m, "Emissive_Strength", 1.5)
mel.update_material_instance(m); eal.save_loaded_asset(m)
print("tuned")
