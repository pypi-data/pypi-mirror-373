import argparse


class SmartFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        # Respect line breaks in help text
        return "".join([indent + line + "\n" for line in text.splitlines()])

    def _split_lines(self, text, width):
        # Respect line breaks in help text
        return text.splitlines()
