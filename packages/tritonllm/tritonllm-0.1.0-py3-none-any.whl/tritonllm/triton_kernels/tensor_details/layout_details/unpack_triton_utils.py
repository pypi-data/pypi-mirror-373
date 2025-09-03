import triton
import triton.language as tl

@triton.jit
def _unpack_fp4_to_bf16_triton_hopper_and_later(x):
    # H100 support with mul.bf16x2
    r0, r1 = tl.inline_asm_elementwise(
        r"""
        {
            .reg .b32 b, c, d<7>, scale;
            .reg .b32 bias;
            mov.b32 bias, 0x7e807e80; // 2 ** 126 == 2 ** (bias_bf16 - bias_fp2)
            // We add the missing bias to the scale directly
            and.b32 $0, $4, 0b10000001110000001000000111000000;
            mul.bf16x2 $0, $0, bias;
            shl.b32 b, $4, 3;
            and.b32 $1, b,  0b10000001110000001000000111000000;
            mul.bf16x2 $1, $1, bias;
            shl.b32 c, $4, 6;
            and.b32 $2, c,  0b10000001110000001000000111000000;
            mul.bf16x2 $2, $2, bias;
            // Unpack last two elements
            shl.b32 d0, $4, 1;
            and.b32 d1, d0, 0b10000000000000001000000000000000;
            shr.b32 d2, $4, 3;
            and.b32 d3, d2, 0b00000001100000000000000110000000;
            or.b32 d4, d1, d3;
            shr.b32 d5, $4, 7;
            and.b32 d6, d5, 0b00000000010000000000000001000000;
            or.b32 $3, d4, d6;
            mul.bf16x2 $3, $3, bias;
        }
        """,
        constraints="=r,=r,=r,=r,r",
        args=[x],
        dtype=(tl.bfloat16, tl.bfloat16),
        is_pure=True,
        pack=4,
    )
    # Concat each pack of 4
    x = tl.join(r0, r1)
    x = x.reshape(x.shape[0], x.shape[1] // 4, 4, x.shape[2])
    x = x.trans(0, 1, 3, 2)
    x = x.reshape(x.shape[0], x.shape[1] * x.shape[2] * x.shape[3])
    return x


@triton.jit
def _unpack_fp4_to_bf16_triton_before_hopper(x):
    # Ampere support with fmul
    r0, r1 = tl.inline_asm_elementwise(
        r"""
        {
            .reg .b32 b, c, d<7>, scale, temp, temp1;
            .reg .b32 bias;
            .reg .b16 low, high, t16;
            mov.b32 bias, 0x7e807e80; // 2 ** 126 == 2 ** (bias_bf16 - bias_fp2)
            // We add the missing bias to the scale directly
            and.b32 $0, $4, 0b10000001110000001000000111000000;
            cvt.u16.u32 low, $0;
            cvt.u16.u32 t16, bias;
            cvt.f32.bf16 temp, low;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 low, temp;
            shr.u32 temp, $0, 16;
            cvt.u16.u32 high, temp;
            shr.u32 temp, bias, 16;
            cvt.u16.u32 t16, temp;
            cvt.f32.bf16 temp, high;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 high, temp;
            cvt.u32.u16 $0, low;
            cvt.u32.u16 temp, high;
            shl.b32 temp, temp, 16;
            or.b32 $0, $0, temp;
            shl.b32 b, $4, 3;
            and.b32 $1, b,  0b10000001110000001000000111000000;
            cvt.u16.u32 low, $1;
            cvt.u16.u32 t16, bias;
            cvt.f32.bf16 temp, low;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 low, temp;
            shr.u32 temp, $1, 16;
            cvt.u16.u32 high, temp;
            shr.u32 temp, bias, 16;
            cvt.u16.u32 t16, temp;
            cvt.f32.bf16 temp, high;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 high, temp;
            cvt.u32.u16 $1, low;
            cvt.u32.u16 temp, high;
            shl.b32 temp, temp, 16;
            or.b32 $1, $1, temp;
            shl.b32 c, $4, 6;
            and.b32 $2, c,  0b10000001110000001000000111000000;
            cvt.u16.u32 low, $2;
            cvt.u16.u32 t16, bias;
            cvt.f32.bf16 temp, low;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 low, temp;
            shr.u32 temp, $2, 16;
            cvt.u16.u32 high, temp;
            shr.u32 temp, bias, 16;
            cvt.u16.u32 t16, temp;
            cvt.f32.bf16 temp, high;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 high, temp;
            cvt.u32.u16 $2, low;
            cvt.u32.u16 temp, high;
            shl.b32 temp, temp, 16;
            or.b32 $2, $2, temp;
            // Unpack last two elements
            shl.b32 d0, $4, 1;
            and.b32 d1, d0, 0b10000000000000001000000000000000;
            shr.b32 d2, $4, 3;
            and.b32 d3, d2, 0b00000001100000000000000110000000;
            or.b32 d4, d1, d3;
            shr.b32 d5, $4, 7;
            and.b32 d6, d5, 0b00000000010000000000000001000000;
            or.b32 $3, d4, d6;
            cvt.u16.u32 low, $3;
            cvt.u16.u32 t16, bias;
            cvt.f32.bf16 temp, low;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 low, temp;
            shr.u32 temp, $3, 16;
            cvt.u16.u32 high, temp;
            shr.u32 temp, bias, 16;
            cvt.u16.u32 t16, temp;
            cvt.f32.bf16 temp, high;
            cvt.f32.bf16 temp1, t16;
            mul.f32 temp, temp, temp1;
            cvt.rn.bf16.f32 high, temp;
            cvt.u32.u16 $3, low;
            cvt.u32.u16 temp, high;
            shl.b32 temp, temp, 16;
            or.b32 $3, $3, temp;
        }
        """,
        constraints="=r,=r,=r,=r,r",
        args=[x],
        dtype=(tl.bfloat16, tl.bfloat16),
        is_pure=True,
        pack=4,
    )
    # Concat each pack of 4
    x = tl.join(r0, r1)
    x = x.reshape(x.shape[0], x.shape[1] // 4, 4, x.shape[2])
    x = x.trans(0, 1, 3, 2)
    x = x.reshape(x.shape[0], x.shape[1] * x.shape[2] * x.shape[3])
    return x
