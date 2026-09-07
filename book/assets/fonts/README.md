# Bundled fonts

These unmodified fonts are bundled so the Arabic edition can be rebuilt offline
without relying on fonts installed on a particular computer.

| File | Family | Upstream distribution used |
| --- | --- | --- |
| `Amiri-Regular.ttf` | Amiri, regular | `@expo-google-fonts/amiri@0.4.1`, `400Regular/Amiri_400Regular.ttf` |
| `Amiri-Bold.ttf` | Amiri, bold | `@expo-google-fonts/amiri@0.4.1`, `700Bold/Amiri_700Bold.ttf` |
| `FiraMono-Regular.ttf` | Fira Mono, regular | `@expo-google-fonts/fira-mono@0.4.1`, `400Regular/FiraMono_400Regular.ttf` |

The upstream font licenses are preserved verbatim in `Amiri-OFL.txt` and
`FiraMono-OFL.txt`. Both use the SIL Open Font License 1.1. These licenses cover
the fonts only, not the source book or its Arabic adaptation.

- Amiri upstream: https://github.com/aliftype/amiri
- Fira upstream: https://github.com/mozilla/Fira
- Distribution metadata: https://www.npmjs.com/package/@expo-google-fonts/amiri
  and https://www.npmjs.com/package/@expo-google-fonts/fira-mono

No font download occurs during the book build. npm is not required to rebuild it.
