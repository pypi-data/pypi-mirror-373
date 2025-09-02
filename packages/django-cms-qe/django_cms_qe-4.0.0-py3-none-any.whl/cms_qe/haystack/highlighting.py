import unicodedata

from haystack.utils.highlighting import Highlighter


def strip_accents(text: str) -> str:
    """Strip accents."""
    return "".join([unicodedata.normalize("NFKD", char)[0] for char in text])


class HaystackHighlighter(Highlighter):
    """Haystack Highlighter."""

    # https://github.com/django-haystack/django-haystack/blob/v3.2.1/haystack/utils/highlighting.py#L32
    def find_highlightable_words(self):
        # Use a set so we only do this once per unique word.
        word_positions = {}

        # Pre-compute the length.
        end_offset = len(self.text_block)
        lower_text_block = self.text_block.lower()
        ascii_text_block = strip_accents(lower_text_block)

        for word in self.query_words:
            if word not in word_positions:
                word_positions[word] = []

            start_offset = 0

            while start_offset < end_offset:
                next_offset = lower_text_block.find(word, start_offset, end_offset)
                if next_offset == -1:
                    next_offset = ascii_text_block.find(word, start_offset, end_offset)

                # If we get a -1 out of find, it wasn't found. Bomb out and
                # start the next word.
                if next_offset == -1:
                    break

                word_positions[word].append(next_offset)
                start_offset = next_offset + len(word)

        return word_positions

    # pylint: disable=too-many-locals
    def render_html(self, highlight_locations=None, start_offset=None, end_offset=None):
        # Start by chopping the block down to the proper window.
        text = self.text_block[start_offset:end_offset]

        # Invert highlight_locations to a location -> term list
        term_list = []

        for term, locations in highlight_locations.items():
            term_list += [(loc - start_offset, term) for loc in locations]

        loc_to_term = sorted(term_list)

        # Prepare the highlight template
        if self.css_class:
            hl_start = f'<{self.html_tag} class="{self.css_class}">'
        else:
            hl_start = f"<{self.html_tag}>"

        hl_end = f"</{self.html_tag}>"

        # Copy the part from the start of the string to the first match,
        # and there replace the match with a highlighted version.
        highlighted_chunk = ""
        matched_so_far = 0
        prev = 0
        prev_str = ""

        for cur, cur_str in loc_to_term:
            # This can be in a different case than cur_str
            actual_term = text[cur:cur + len(cur_str)]

            # Handle incorrect highlight_locations by first checking for the term
            actual_term_lower = actual_term.lower()
            if actual_term_lower == cur_str or strip_accents(actual_term_lower) == cur_str:
                if cur < prev + len(prev_str):
                    continue

                highlighted_chunk += (
                    text[prev + len(prev_str):cur] + hl_start + actual_term + hl_end
                )
                prev = cur
                prev_str = cur_str

                # Keep track of how far we've copied so far, for the last step
                matched_so_far = cur + len(actual_term)

        # Don't forget the chunk after the last term
        highlighted_chunk += text[matched_so_far:]

        if start_offset > 0:
            highlighted_chunk = f"...{highlighted_chunk}"

        if end_offset < len(self.text_block):
            highlighted_chunk = f"{highlighted_chunk}..."

        return highlighted_chunk
