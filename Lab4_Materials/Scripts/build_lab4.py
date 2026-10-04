"""Lab 4 - builds M_MasterProp (2.1/2.2, 3.x, 5.1-5.5) plus instances and a demo level."""
import unreal

mel = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
FOLDER = "/Game/Lab4"
MP = unreal.MaterialProperty


def fresh(name, cls, factory):
    path = f"{FOLDER}/{name}"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)  # rebuild in place (deleting a referenced asset fails)
    return tools.create_asset(name, FOLDER, cls, factory)


def node(mat, cls, x, y, **props):
    n = mel.create_material_expression(mat, cls, x - 1400, y - 300)  # keep graph left of the output node
    for k, v in props.items():
        n.set_editor_property(k, v)
    return n


def tex_node(mat, tex_path, x, y):
    tex = unreal.load_asset(tex_path)
    n = node(mat, unreal.MaterialExpressionTextureSample, x, y, texture=tex)
    cs = tex.get_editor_property("compression_settings")
    srgb = tex.get_editor_property("srgb")
    TC, ST = unreal.TextureCompressionSettings, unreal.MaterialSamplerType
    if cs == TC.TC_NORMALMAP:
        st = ST.SAMPLERTYPE_NORMAL
    elif cs == TC.TC_MASKS:
        st = ST.SAMPLERTYPE_MASKS
    elif cs in (TC.TC_GRAYSCALE, TC.TC_ALPHA):
        st = ST.SAMPLERTYPE_GRAYSCALE if srgb else ST.SAMPLERTYPE_LINEAR_GRAYSCALE
    else:
        st = ST.SAMPLERTYPE_COLOR if srgb else ST.SAMPLERTYPE_LINEAR_COLOR
    n.set_editor_property("sampler_type", st)
    return n


def comment(mat, text, x, y, w, h, color):
    pass  # comment box size is not exposed to Python; key nodes get a desc instead


def link(a, a_out, b, b_in):
    ok = mel.connect_material_expressions(a, a_out, b, b_in)
    if not ok:
        unreal.log_error(f"LAB4 link failed: {a.get_name()}.{a_out} -> {b.get_name()}.{b_in}")


def C3(r, g, b):
    return unreal.LinearColor(r, g, b, 1.0)


# ---------------------------------------------------------------- master material
mat = fresh("M_MasterProp", unreal.Material, unreal.MaterialFactoryNew())
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(mat)
mel.delete_all_material_expressions(mat)

# 2.1 basic texture setup
comment(mat, "2.1 Base Color x Color_Tint  /  ORM split + Roughness_Multiplier", -1500, -420, 760, 760, C3(0.2, 0.4, 1))
t_base = tex_node(mat, "/Engine/EngineMaterials/DefaultDiffuse", -1460, -360)
p_tint = node(mat, unreal.MaterialExpressionVectorParameter, -1460, -120,
              parameter_name="Color_Tint", default_value=C3(1, 1, 1), group="Surface")
m_tint = node(mat, unreal.MaterialExpressionMultiply, -1060, -260)
link(t_base, "RGB", m_tint, "A")
link(p_tint, "", m_tint, "B")

t_orm = tex_node(mat, "/Engine/EngineMaterials/T_Default_Material_Grid_M", -1460, 40)
p_rough = node(mat, unreal.MaterialExpressionScalarParameter, -1460, 260,
               parameter_name="Roughness_Multiplier", default_value=1.0, group="Surface")
m_rough = node(mat, unreal.MaterialExpressionMultiply, -1060, 160)
link(t_orm, "G", m_rough, "A")
link(p_rough, "", m_rough, "B")
mel.connect_material_property(t_orm, "R", MP.MP_AMBIENT_OCCLUSION)
mel.connect_material_property(m_rough, "", MP.MP_ROUGHNESS)
mel.connect_material_property(t_orm, "B", MP.MP_METALLIC)

# 3.1 / 3.2 mask + lerp
comment(mat, "3.1-3.2 Mask (R) blends Clean -> Rust via Lerp", -700, -420, 560, 420, C3(0.6, 0.4, 0.1))
t_mask = tex_node(mat, "/Engine/EngineMaterials/T_Default_MacroVariation", -660, -360)
c_rust = node(mat, unreal.MaterialExpressionConstant3Vector, -660, -120, constant=C3(0.55, 0.18, 0.04))
lerp = node(mat, unreal.MaterialExpressionLinearInterpolate, -360, -260)
link(m_tint, "", lerp, "A")
link(c_rust, "", lerp, "B")
link(t_mask, "R", lerp, "Alpha")
mel.connect_material_property(lerp, "", MP.MP_BASE_COLOR)

# 5.4 pulse: Time -> Sine -> +1 -> *0.5
comment(mat, "5.4 Pulse over time: (Sine(Time) + 1) * 0.5  =>  0..1", -1500, 420, 1000, 300, C3(0.8, 0.2, 0.8))
n_time = node(mat, unreal.MaterialExpressionTime, -1460, 500)
n_sine = node(mat, unreal.MaterialExpressionSine, -1260, 500, period=2.0)
c_one = node(mat, unreal.MaterialExpressionConstant, -1260, 600, r=1.0)
a_shift = node(mat, unreal.MaterialExpressionAdd, -1060, 520)
c_half = node(mat, unreal.MaterialExpressionConstant, -1060, 620, r=0.5)
m_pulse = node(mat, unreal.MaterialExpressionMultiply, -860, 540)
link(n_time, "", n_sine, "")
link(n_sine, "", a_shift, "A")
link(c_one, "", a_shift, "B")
link(a_shift, "", m_pulse, "A")
link(c_half, "", m_pulse, "B")

# 5.1 basic glow (strength now driven by the 5.4 pulse)
comment(mat, "5.1 Emissive: Cyan x (Emissive_Strength x Pulse)", -460, 420, 620, 300, C3(0.1, 0.8, 0.9))
p_strength = node(mat, unreal.MaterialExpressionScalarParameter, -420, 480,
                  parameter_name="Emissive_Strength", default_value=5.0, group="Emissive")
m_strength_pulse = node(mat, unreal.MaterialExpressionMultiply, -200, 540)
link(p_strength, "", m_strength_pulse, "A")
link(m_pulse, "", m_strength_pulse, "B")
c_cyan = node(mat, unreal.MaterialExpressionConstant3Vector, -420, 620, constant=C3(0.0, 0.85, 1.0))
m_emissive = node(mat, unreal.MaterialExpressionMultiply, 0, 560)
link(c_cyan, "", m_emissive, "A")
link(m_strength_pulse, "", m_emissive, "B")

# 5.2 masked emissive
comment(mat, "5.2 Mask (R) x Emissive", 200, 420, 260, 300, C3(0.1, 0.8, 0.3))
m_masked = node(mat, unreal.MaterialExpressionMultiply, 240, 520)
link(t_mask, "R", m_masked, "A")
link(m_emissive, "", m_masked, "B")

# 5.3 fresnel edge glow
comment(mat, "5.3 Fresnel edge glow (Exponent 3) x Orange, Added to emissive", -460, 760, 1000, 300, C3(1, 0.5, 0))
n_fresnel = node(mat, unreal.MaterialExpressionFresnel, -420, 820, exponent=3.0, base_reflect_fraction=0.0)
c_rim = node(mat, unreal.MaterialExpressionConstant3Vector, -420, 960, constant=C3(4.0, 1.2, 0.0))
m_fresnel = node(mat, unreal.MaterialExpressionMultiply, -100, 880)
link(n_fresnel, "", m_fresnel, "A")
link(c_rim, "", m_fresnel, "B")
a_emissive = node(mat, unreal.MaterialExpressionAdd, 360, 760)
link(m_masked, "", a_emissive, "A")
link(m_fresnel, "", a_emissive, "B")

# 2.2 / 5.5 static switch
comment(mat, "2.2 / 5.5 Static Switch: Enable_Emissive (True = glow, False = black)", 560, 600, 520, 360, C3(1, 0.1, 0.1))
c_black = node(mat, unreal.MaterialExpressionConstant3Vector, 600, 840, constant=C3(0, 0, 0))
sw = node(mat, unreal.MaterialExpressionStaticSwitchParameter, 840, 700,
          parameter_name="Enable_Emissive", default_value=True, group="Emissive")
link(a_emissive, "", sw, "True")
link(c_black, "", sw, "False")
mel.connect_material_property(sw, "", MP.MP_EMISSIVE_COLOR)

for n, d in [(n_fresnel, "5.3 Fresnel edge glow"), (a_emissive, "5.3 Add Fresnel to emissive"),
             (n_time, "5.4 Pulse: Time"), (m_pulse, "5.4 (Sine+1)*0.5 = 0..1 pulse"),
             (m_strength_pulse, "5.4 Emissive_Strength x Pulse"), (m_masked, "5.2 Mask x Emissive"),
             (sw, "5.5 Static Switch -> Emissive"), (lerp, "3.2 Mask Lerp")]:
    n.set_editor_property("desc", d)

mel.recompile_material(mat)
eal.save_loaded_asset(mat)


# ---------------------------------------------------------------- instances
def make_mi(name, vecs=None, scalars=None, switches=None):
    mi = fresh(name, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    for k, v in (vecs or {}).items():
        mel.set_material_instance_vector_parameter_value(mi, k, v)
    for k, v in (scalars or {}).items():
        mel.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (switches or {}).items():
        mel.set_material_instance_static_switch_parameter_value(mi, k, v)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    return mi


mi_clean = make_mi("MI_Prop_Clean", {"Color_Tint": C3(0.9, 0.9, 0.85)}, {"Roughness_Multiplier": 0.6})
mi_worn = make_mi("MI_Prop_Worn", {"Color_Tint": C3(0.35, 0.3, 0.25)}, {"Roughness_Multiplier": 1.4})
mi_on = make_mi("MI_Emissive_On", switches={"Enable_Emissive": True})
mi_off = make_mi("MI_Emissive_Off", switches={"Enable_Emissive": False})

# ---------------------------------------------------------------- demo level
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if eal.does_asset_exist(f"{FOLDER}/L_Lab4"):
    les.load_level(f"{FOLDER}/L_Lab4")
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("Lab4_"):
            eas.destroy_actor(a)
else:
    les.new_level_from_template(f"{FOLDER}/L_Lab4", "/Engine/Maps/Templates/Template_Default")

sphere = unreal.load_asset("/Engine/BasicShapes/Sphere")
for i, (label, mi) in enumerate([("Clean", mi_clean), ("Worn", mi_worn),
                                 ("Emissive ON", mi_on), ("Emissive OFF", mi_off)]):
    loc = unreal.Vector(600, -450 + i * 300, 150)
    a = eas.spawn_actor_from_object(sphere, loc)
    a.set_actor_label(f"Lab4_{label.replace(' ', '_')}")
    a.set_actor_scale3d(unreal.Vector(2, 2, 2))
    a.static_mesh_component.set_material(0, mi)
    t = eas.spawn_actor_from_class(unreal.TextRenderActor, loc + unreal.Vector(0, 0, 150))
    t.set_actor_label(f"Lab4_Label_{i}")
    t.set_actor_rotation(unreal.Rotator(0, 180, 0), False)
    tr = t.text_render
    tr.set_text(label)
    tr.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    tr.set_world_size(40)
    tr.set_text_render_color(unreal.Color(255, 255, 255, 255))

les.save_current_level()
unreal.log("LAB4 BUILD DONE")
