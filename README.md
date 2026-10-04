# Lab 4 – Sections 5.3, 5.4, 5.5 (Unreal Engine 5.8)

Master material `M_MasterProp` (in `Lab4_Materials/Content/Lab4`) with:

- **5.3 Fresnel edge glow:** a Fresnel node (Exponent 3) × an orange emissive colour, added to the masked emissive with an Add node.
- **5.4 Pulsing emissive:** Time → Sine (period 2) → Add 1 → Multiply 0.5, which gives a 0–1 pulse. The pulse is multiplied into `Emissive_Strength` (default 5).
- **5.5 Static Switch:** `Enable_Emissive`. True gets the full emissive chain and False gets a black Constant3Vector. Its output goes to Emissive Color. Two instances, `MI_Emissive_On` and `MI_Emissive_Off`, toggle it independently.

The graph is built with `Lab4_Materials/Scripts/build_lab4.py` (UE Python).

## Screenshots
| File | Shows |
|---|---|
| `screenshots/01_Master_Material_Full_Graph.png` | Full master graph with the Static Switch and the completed emissive chain |
| `screenshots/04_Pulse_t1..t4.png` | Pulsing emissive over time (t1 peak glow → t3/t4 low, with only the Fresnel rim left) |
| `screenshots/05_Level_Instances.png` | Instances side by side. Emissive ON has the cyan masked glow and the orange Fresnel rim. Emissive OFF has no glow. |

## Fresnel vs mask
The mask texture decides *where on the surface* the glow appears. It is a fixed, painted pattern on the UVs, so the cyan only shows in its white areas. The Fresnel node decides glow by *viewing angle*: it is strongest at the silhouette edges and moves as the camera or object rotates. Adding the two gives a patterned surface glow plus a rim light.
