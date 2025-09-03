struct Normalization {
    // data min
    float min;
    // data max
    float max;
    // 0: no normalization, 1: project 0..1 to min..max
    int mode;
};

struct Domain {
    float min;
    float max;
};

uniform sampler2D textureA;
uniform Normalization normA;
uniform sampler2D textureB;
uniform Normalization normB;

uniform int mode;
uniform float lateral;
uniform float tilt;
uniform float sizeCoef;
uniform Domain domain;
uniform float verticalSeparator;
uniform int kernelSize;
uniform float kernelCoefs[9];

in vec2 texCoord;

vec2 rotatedVec2(vec2 uv, vec2 axis, float angle)
{
	mat2 m = mat2(
        vec2(cos(angle), -sin(angle)),
		vec2(sin(angle), cos(angle))
    );
    return (uv - axis) * m + axis;
}

/**
 * Convert a normalized texture into final data.
 */
float denormalize(float p, Normalization norm) {
    if (norm.mode == 0) {
        return p;
    }
    if (norm.mode == 1) {
        return norm.min + p * (norm.max - norm.min);
    }
    return -1.0;
}

float getPixel(
    vec2 coord,
    sampler2D textureN,
    Normalization normN,
    float tilt
) {
    ivec2 itexSize = textureSize(textureN, 0);
    vec2 texSize = vec2(itexSize) * 0.5;
    coord = (coord - vec2(0.5, 0.5)) * texSize;
    coord = rotatedVec2(coord, vec2(0.0, 0.0), tilt);
    coord = (coord / texSize) + vec2(0.5, 0.5);

    if (coord.x < 0.0) { return -1.0; }
    if (coord.x > 1.0) { return -1.0; }
    if (coord.y < 0.0) { return -1.0; }
    if (coord.y > 1.0) { return -1.0; }
    float p = texture2D(textureN, coord).r;
    p = denormalize(p, normN);
    p = (p - domain.min) / (domain.max - domain.min);
    p = clamp(p, 0.0, 1.0);
    return p;
}

float getFilteredPixel(
    vec2 coord,
    sampler2D textureN,
    Normalization normN,
    float tilt
) {
    ivec2 itexSize = textureSize(textureN, 0);
    vec2 texSize = vec2(itexSize) * 0.5;
    coord = (coord - vec2(0.5, 0.5)) * texSize;

    float cum_p = 0.0;
    int cum_coef = 0;
    int i = 0;

    for (int x = 0; x < kernelSize; x++) {
        for (int y = 0; y < kernelSize; y++) {
            vec2 xy = vec2(x - (kernelSize - 1) / 2, y - (kernelSize - 1) / 2);
            vec2 coord2 = rotatedVec2(coord + xy * 1.0, vec2(0.0, 0.0), tilt);
            coord2 = (coord2 / texSize) + vec2(0.5, 0.5);

            float coef = kernelCoefs[i];
            i++;

            if (coord2.x < 0.0) { continue; }
            if (coord2.x > 1.0) { continue; }
            if (coord2.y < 0.0) { continue; }
            if (coord2.y > 1.0) { continue; }

            float p = texture2D(textureN, coord2).r;
            p = denormalize(p, normN);
            p = (p - domain.min) / (domain.max - domain.min);
            p = clamp(p, 0.0, 1.0);
            cum_p += p * coef;
            cum_coef++;
        }
    }
    if (cum_coef == 0) {
        return -1.0;
    }
    return clamp(cum_p, 0.0, 1.0);
}

vec4 colorize_a(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    return vec4(a, a, a, 1.0);
}

vec4 colorize_b(float a, float b) {
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    return vec4(b, b, b, 1.0);
}

vec4 colorize_mul(float a, float b) {
    // multiply
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = a * b;
    return vec4(m, m, m, 1.0);
}

vec4 colorize_mul_color(float a, float b) {
    // multiply
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = a * b;
    return vec4(m, (b + a ) * 0.5,  b, 1.0);
}

vec4 colorize_diff(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float i = 0.5 + (a - b);
    return vec4(i, i, i, 1.0);
}

vec4 colorize_diff_color(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }

    float i = (a - b) * 10.0;
    if (i > 1.0) {
        i = 1.0;
    }

    float da = (i > 0.0) ? i : 0.0;
    float db = (i < 0.0) ? -i : 0.0;
    return vec4(1.0 - da - db * 0.5, 1.0, 1.0 - db * 0.5, 1.0);
}

vec4 colorize_min(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = min(a, b);
    return vec4(m, m, m, 1.0);
}

vec4 colorize_min_color(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = min(a, b);
    return vec4(m, (b + a ) * 0.5,  b, 1.0);
}

vec4 colorize_max(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = max(a, b);
    return vec4(m, m, m, 1.0);
}

vec4 colorize_max_color(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float m = max(a, b);
    return vec4(min(a, b), m, a, 1.0);
}

vec4 colorize_error(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float error = sqrt(abs(a - b));
    float i = 1.0 - error;
    return vec4(i, i, i, 1.0);
}

vec4 colorize_error_color(float a, float b) {
    if (a < 0.0) {
        return vec4(0.0, b, 0.0, 0.75);
    }
    if (b < 0.0) {
        return vec4(0.0, a, a, 0.75);
    }
    float d = a - b;
    float s = sign(d);

    float i = 1.0 - abs(d);
    i = i * i * i;
    float da = (s > 0.0) ? i : 0.0;
    float db = (s < 0.0) ? i : 0.0;
    return vec4(1.0 - da - db * 0.6, 1.0, 1.0 - db * 0.6, 1.0);
}

vec4 colorize_hspliter(float a, float b) {
    ivec2 itexSize = textureSize(textureA, 0);
    vec2 texSize = vec2(itexSize);
    if (-((texCoord.y - 0.5) * texSize.y * sizeCoef) < verticalSeparator) {
        if (a < 0.0) {
            discard;
        }
        return vec4(a, a, a, 1.0);
    } else {
        if (b < 0.0) {
            discard;
        }
        return vec4(b, b, b, 1.0);
    }
}

vec4 colorize_hspliter_color(float a, float b) {
    ivec2 itexSize = textureSize(textureA, 0);
    vec2 texSize = vec2(itexSize);
    if (-((texCoord.y - 0.5) * texSize.y * sizeCoef) < verticalSeparator) {
        if (a < 0.0) {
            discard;
        }
        return vec4(0.0, a, a, 1.0);
    } else {
        if (b < 0.0) {
            discard;
        }
        return vec4(0.0, b, 0.0, 1.0);
    }
}

vec4 colorize_custom_func(float a, float b) {
    // CUSTOM FUNC INJECTION //;
    return vec4(0.0, 0.0, 0.0, 1.0);
}


/*
// error without killing the content
    float error = sqrt(abs(a - b));
    float i = 1.0 - error;
    float m = 1.0 - max(a,b);
    return vec4(i, 1.0 - a, 1.0 - b, 1.0);


*/


float pixelToTexture(float pixel, sampler2D textureN) {
    ivec2 itexSize = textureSize(textureN, 0);
    vec2 texSize = vec2(itexSize);
    float size = max(texSize.x, texSize.y);
    return pixel / size;
}

void main() {
    float lateralTex = pixelToTexture(lateral * 0.5, textureA);
    vec2 normal = vec2(texCoord.x + lateralTex, texCoord.y);
    vec2 mirror = vec2(1.0 - texCoord.x + lateralTex, texCoord.y);
    float a;
    float b;
    if (kernelSize == 0) {
        a = getPixel(normal, textureA, normA, tilt);
        b = getPixel(mirror, textureB, normB, -tilt);
    } else {
        a = getFilteredPixel(normal, textureA, normA, tilt);
        b = getFilteredPixel(mirror, textureB, normB, -tilt);
    }

    if (a < 0.0 && b < 0.0) {
        discard;
    }

    vec4 c;
    switch (mode) {
        case 0:
            c = colorize_a(a, b);
            break;
        case 1:
            c = colorize_b(a, b);
            break;

        case 100:
            c = colorize_diff(a, b);
            break;
        case 101:
            c = colorize_error(a, b);
            break;
        case 102:
            c = colorize_max(a, b);
            break;
        case 103:
            c = colorize_min(a, b);
            break;
        case 104:
            c = colorize_mul(a, b);
            break;
        case 105:
            c = colorize_hspliter(a, b);
            break;

        case 200:
            c = colorize_diff_color(a, b);
            break;
        case 201:
            c = colorize_error_color(a, b);
            break;
        case 202:
            c = colorize_max_color(a, b);
            break;
        case 203:
            c = colorize_min_color(a, b);
            break;
        case 204:
            c = colorize_mul_color(a, b);
            break;
        case 205:
            c = colorize_hspliter_color(a, b);
            break;

        case 300:
            c = colorize_custom_func(a, b);
            break;
        default:
            c = vec4(1.0, 0.0, 0.0, 1.0);
    }
    gl_FragColor = c;
}
