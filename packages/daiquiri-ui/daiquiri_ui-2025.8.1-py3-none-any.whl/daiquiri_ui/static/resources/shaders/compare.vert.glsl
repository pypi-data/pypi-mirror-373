uniform sampler2D proj0Map;
uniform float sizeCoef;
out vec2 texCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    // texCoord = ((gl_Position.xy - vec2(-2.5)) / 5.0);
    ivec2 itexSize = textureSize(proj0Map, 0);
    vec2 texSize = vec2(itexSize);
    texCoord = (vec2(position.x, -position.y) / (texSize*sizeCoef)) + 0.5;
}
