# Meihua Rules

- Use Beijing time.
- Convert the current hour into the 12 shichen scale.
- Upper hexagram: `(year + month + day) % 8`, zero maps to 8.
- Lower hexagram: `(year + month + day + shichen) % 8`, zero maps to 8.
- Moving line: `(year + month + day + shichen) % 6`, zero maps to 6.
- Body/use is determined by whether the moving line sits in the upper or lower trigram.

