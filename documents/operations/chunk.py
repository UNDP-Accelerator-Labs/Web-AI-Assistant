"""
Inspired by: https://stackoverflow.com/questions/48381870/a-better-way-to-split-a-sequence-in-chunks-with-overlaps
"""

def chunk (text, size, overlap):
	if size < 1 or overlap < 0:
		raise ValueError('size must be >= 1 and overlap >= 0')

	chunks = []

	for i in range(0, len(text) - overlap, size - overlap):			
		chunks.append(text[i:i + size])

	return chunks