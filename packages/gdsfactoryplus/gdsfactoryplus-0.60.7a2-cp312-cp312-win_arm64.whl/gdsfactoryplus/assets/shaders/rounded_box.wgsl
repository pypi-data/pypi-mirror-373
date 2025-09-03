#import bevy_sprite::mesh2d_functions

struct RoundedBoxMaterial {
    @location(0)
    color: vec4<f32>,
    @location(1)
    border_width: f32,
    @location(2)
    border_color: vec4<f32>,
    @location(3)
    corner_radius: f32,
    @location(4)
    outline_width: f32,
    @location(5)
    outline_color: vec4<f32>
}

struct Vertex {
    @builtin(instance_index) instance_index: u32,
    @location(0) position: vec3<f32>,
    @location(1) uv: vec2<f32>,
}

struct VertexOutput {
    @builtin(position) clip_position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) size: vec2<f32>, 
}

@group(2) @binding(0) var<uniform> material: RoundedBoxMaterial;

@vertex
fn vertex(vertex: Vertex) -> VertexOutput {
    var out: VertexOutput;

    let tag = mesh2d_functions::get_tag(vertex.instance_index);

    // Decode the tag: first 16 bits for width, last 16 bits for height
    let width = f32(tag >> 16u);
    let height = f32(tag & 0xFFFFu);
    let size = vec2<f32>(width, height) + material.outline_width * 2.0;

    let scaled_pos = vec4<f32>(vertex.position.xy * size, vertex.position.z, 1.0);

    let world = mesh2d_functions::get_world_from_local(vertex.instance_index);

    out.clip_position = mesh2d_functions::mesh2d_position_local_to_clip(
        world,
        scaled_pos,
    );

    out.uv = vertex.uv;
    out.size = size; // Pass the size to
    return out;
}

fn sd_rounded_box(point: vec2<f32>, size: vec2<f32>, corner_radii: vec4<f32>) -> f32 {
    // If 0.0 < y then select bottom left (w) and bottom right corner radius (z).
    // Else select top left (x) and top right corner radius (y).
    let rs = select(corner_radii.xy, corner_radii.wz, 0.0 < point.y);
    // w and z are swapped above so that both pairs are in left to right order, otherwise this second 
    // select statement would return the incorrect value for the bottom pair.
    let radius = select(rs.x, rs.y, 0.0 < point.x);
    // Vector from the corner closest to the point, to the point.
    let corner_to_point = abs(point) - 0.5 * size;
    // Vector from the center of the radius circle to the point.
    let q = corner_to_point + radius;
    // Length from center of the radius circle to the point, zeros a component if the point is not 
    // within the quadrant of the radius circle that is part of the curved corner.
    let l = length(max(q, vec2(0.0)));
    let m = min(max(q.x, q.y), 0.0);
    return l + m - radius;
}

fn sd_inset_rounded_box(point: vec2<f32>, size: vec2<f32>, radius: vec4<f32>, inset: vec4<f32>) -> f32 {
    let inner_size = size - inset.xy - inset.zw;
    let inner_center = inset.xy + 0.5 * inner_size - 0.5 * size;
    let inner_point = point - inner_center;

    var r = radius;

    // Top left corner.
    r.x = r.x - max(inset.x, inset.y);

    // Top right corner.
    r.y = r.y - max(inset.z, inset.y);

    // Bottom right corner.
    r.z = r.z - max(inset.z, inset.w); 

    // Bottom left corner.
    r.w = r.w - max(inset.x, inset.w);

    let half_size = inner_size * 0.5;
    let min_size = min(half_size.x, half_size.y);

    r = min(max(r, vec4(0.0)), vec4<f32>(min_size));

    return sd_rounded_box(inner_point, inner_size, r);
}

fn antialias(distance: f32) -> f32 {
    // Using the fwidth(distance) was causing artifacts, so just use the distance.
    return saturate(0.5 - distance);
}

@fragment
fn fragment(in: VertexOutput) -> @location(0) vec4<f32> {
    // Convert UV coordinates to centered coordinates
    let uv = in.uv * 2.0 - 1.0;
    
    // Scale by size
    let size = in.size;
    let pos = uv * size * 0.5;
    let corner_radius = material.corner_radius;
    let color = material.color;
    let border_color = material.border_color;
    let border_width = material.border_width;
    let outline_width = material.outline_width;
    let outline_color = material.outline_color;
    // Signed distances. The magnitude is the distance of the point from the edge of the shape.
    // * Negative values indicate that the point is inside the shape.
    // * Zero values indicate the point is on the edge of the shape.
    // * Positive values indicate the point is outside the shape.

    // Signed distance from the exterior boundary.
    var external_distance = sd_rounded_box(pos, size, vec4(corner_radius + outline_width));

    // If the point is outside the shape, return transparent.
    if (external_distance > 0.0) {
        discard;
    }

    let external_distance_outline = sd_rounded_box(pos, size - outline_width * 2.0, vec4(corner_radius));

    if (external_distance_outline > 0.0) {
        // we are in the outline
        let internal_distance_outline = sd_inset_rounded_box(pos, size - outline_width * 2.0, vec4(corner_radius), 
        vec4(outline_width));

        let outline_distance = max(external_distance, -internal_distance_outline);

        let t = select(1.0 - step(0.0, outline_distance), antialias(outline_distance), external_distance_outline < internal_distance_outline);

        return vec4(outline_color.rgb, saturate(outline_color.a * t));
    }

    external_distance = sd_rounded_box(pos, size - outline_width * 2, vec4(corner_radius));

    // Signed distance from the border's internal edge (the signed distance is negative if the point 
    // is inside the rect but not on the border).
    // If the border size is set to zero, this is the same as the external distance.
    let internal_distance = sd_inset_rounded_box(pos, size - outline_width * 2., vec4(corner_radius), 
        vec4(border_width));

    // Signed distance from the border (the intersection of the rect with its border).
    // Points inside the border have negative signed distance. Any point outside the border, whether 
    // outside the outside edge, or inside the inner edge have positive signed distance.
    let border_distance = max(external_distance, -internal_distance);

    // At external edges with no border, `border_distance` is equal to zero. 
    // This select statement ensures we only perform anti-aliasing where a non-zero width border 
    // is present, otherwise an outline about the external boundary would be drawn even without 
    // a border.
    let t = select(1.0 - step(0.0, border_distance), antialias(border_distance), external_distance < internal_distance);

    if t == 0.0 {
        return color;
    }
    // Blend mode ALPHA_BLENDING is used for UI elements, so we don't premultiply alpha here.
    return vec4(border_color.rgb, saturate(border_color.a * t));
}
