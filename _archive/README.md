# Archived desktop scripts

These two scripts are superseded by later versions in the repository root and are no longer maintained or tested.
They are kept for history. Nothing in the repository imports them.

| Script | Superseded by | Why it is redundant |
|--------|---------------|---------------------|
| `optical_illusion_generator.py` | `optical_illusion_generator_V2.py` | V2 has every pattern and option of the original (3 spirals, interference, 4 illusions) plus more. Every original pattern renders pixel-identically in V2 (checked for all variants, both colour modes, 2026-11-11). Every method of the original app class is also in V2. |
| `enhanced_pattern_generator.py` | `enhanced_pattern_generator_V2.py` | V2 contains the same genetic algorithm, aesthetic analyser, animation parameters and pattern genome (identical code), the same app features (its multi-parameter animation is V2's "multi-animation"), and more generators. Its only generator was a simplified demo spiral: 1000 points over 10*pi*density, Fermat coefficient 0.2, always black on an 8x8 figure. V2's spiral gives the same curves with density/2 (and scale x 2/3 for Fermat). |

To run one anyway: `python _archive/optical_illusion_generator.py` (needs numpy, matplotlib; tkinter).
