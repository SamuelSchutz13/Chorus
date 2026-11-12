from genius import extract_lyrics, html_to_text, norm

assert norm("Evidências (Ao Vivo)") == norm("evidencias") == "evidencias"
assert html_to_text("<div><p>a<br>b</p><p>c</p></div>") == "a\nb\n\nc"

html = """<html><body>
<div data-lyrics-container="true"><div data-exclude-from-selection="true">5 Contributors</div>
[Verse 1]<br><a href="#"><span>Linha um</span></a><br>Linha dois</div>
<div data-lyrics-container="true">Linha três</div>
</body></html>"""

assert extract_lyrics(html) == "[Verse 1]\nLinha um\nLinha doisLinha três", repr(extract_lyrics(html))
assert extract_lyrics("<html><body></body></html>") is None
print("ok")
