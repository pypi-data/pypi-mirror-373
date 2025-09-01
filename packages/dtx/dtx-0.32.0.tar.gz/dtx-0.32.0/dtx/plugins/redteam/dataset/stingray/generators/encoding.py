"""Encoding-based prompt injection

Probes that try to get a model to generate a specific piece of given text
by presenting an encoded version of that text. Attempts to circumvent
safeguards on input filtering.

optional variable: "encoding.payloads" -> a list of payload types to be used
"""

import base64
import binascii
from .base import (BasePromptWithEvalHintGenerator, ThreatClass, ThreatCategory)
from .utils.payload_library import PayloadLibrary
from .utils.encoders import PayloadEncoder
from ..domain.modelio import EvaluationHint
from .utils.encoders import rot13, braille, morse


class BaseEncodingGenerator(BasePromptWithEvalHintGenerator):
    """Mixin for encoding-based injection probes"""

    tags = [
        "avid-effect:security:S0403",
        "owasp:llm01",
        "quality:Security:PromptStability",
        "payload:generic",
    ]
    goal = "make the model say an encoded payload"
    bcp47 = "en"
    doc_uri = "https://kai-greshake.de/posts/llm-malware/#encoded-inline-jailbreak"

    recommended_detector = ["encoding.DecodeMatch", "encoding.DecodeApprox"]
    extended_detectors = [
        "encoding.DecodeApprox",
    ]
    technique="indirect-prompt-injection-encoding"
    threat_class=ThreatClass.DEFENSE_BYPASS
    threat_category=ThreatCategory.PROMPT_INJECTION

    def __init__(self, config=None):
        super().__init__(config=config)
        self.prompts = []
        self.eval_hints = []
        
        plib = PayloadLibrary(self.config.resource_path)
        pencoder = PayloadEncoder()
        
        payload_classes = self.config.generators['techniques'][self.technique]['payload_classes']
        payloads, extra_tags = plib.get_payloads(payload_classes)
        self.tags += extra_tags
        self.prompts, triggers = zip(
            *pencoder.generate_encoded_prompts(payloads, self.encoding_funcs, self.encoding_name)
        )
        
        for term in triggers:
            hint = EvaluationHint(expected_next_words=term)
            self.eval_hints.append(hint)
                        
        # for payload in payloads:
        #     print("\n\nPayload ", payload)
        # for prompt, hint in zip(self.prompts, triggers):
        #     print("\n\tPrompt ", prompt, "\n\tHint", hint)


class InjectBase64(BaseEncodingGenerator):
    """Probe for susceptibility to base64 encoded injections

    Encodes payloads using base64, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [
        base64.b64encode,
        base64.urlsafe_b64encode,
        base64.standard_b64encode,
        binascii.b2a_base64,
    ]
    encoding_name = "BASE64"

    def __init__(self, config=None):
        super().__init__(config)

class InjectBase16(BaseEncodingGenerator):
    """Probe for susceptibility to base16 encoded injections"

    Encodes payloads using base16, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [base64.b16encode]
    encoding_name = "BASE16"

    def __init__(self, config=None):
        super().__init__(config)


class InjectBase32(BaseEncodingGenerator):
    """Probe for susceptibility to base32 encoded injections

    Encodes payloads using base32, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [base64.b32encode]
    encoding_name = "BASE32"

    def __init__(self, config=None):
        super().__init__(config)


class InjectAscii85(BaseEncodingGenerator):
    """Probe for susceptibility to base85 encoded injections

    Encodes payloads using ascii85, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [base64.a85encode, base64.b85encode]
    encoding_name = "ASCII85"

    def __init__(self, config=None):
        super().__init__(config)


class InjectHex(BaseEncodingGenerator):
    """Probe for susceptibility to hex encoded injections

    Encodes payloads using hex, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [binascii.b2a_hex]
    encoding_name = "hex"

    def __init__(self, config=None):
        super().__init__(config)


class InjectQP(BaseEncodingGenerator):
    """Probe for susceptibility to QP encoded injections

    Encodes payloads using quoted-printable, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_funcs = [binascii.b2a_qp]
    encoding_name = "Quoted-Printable"
    active = False  # seems to just pass text right through - when using ascii chars

    def __init__(self, config=None):
        super().__init__(config)

class InjectUU(BaseEncodingGenerator):
    """Probe for susceptibility to UU encoded injections

    Encodes payloads using uuencoding, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_name = "UUencode"

    def UUencode(self, payload):
        hash_chunks = []
        for i in range(0, len(payload), 45):
            test_chunk = payload[i : i + 45]
            hash_chunks.append(binascii.b2a_uu(test_chunk))
        return "".join(map(bytes.decode, hash_chunks))

    def __init__(self, config=None):
        self.encoding_funcs = [self.UUencode]
        super().__init__(config)


class InjectMime(BaseEncodingGenerator):
    """Probe for susceptibility to MIME encoding injections

    Encodes payloads using MIME encoding, and tries a variety of ways of getting the
    target model to repeat & decode them."""

    encoding_name = "MIME"
    active = False  # seems to just pass text right through - when using ascii chars

    def __init__(self, config=None):
        import quopri

        self.encoding_funcs = [quopri.encodestring]
        super().__init__(config)


class InjectROT13(BaseEncodingGenerator):
    """Probe for susceptibility to ROT13 encoding injections

    Encodes payloads using ROT13, and tries a variety of ways of getting the target
    model to repeat & decode them. ROT13 only applies to letters in the English
    alphabet."""

    encoding_funcs = [rot13]
    encoding_name = "ROT13"

    def __init__(self, config=None):
        super().__init__(config)


class InjectBase2048(BaseEncodingGenerator):
    """Probe for susceptibility to Base2048 encoding injections

    Encodes payloads using base2048, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    encoding_name = "BASE2048"

    def __init__(self, config=None):
        import base2048

        self.encoding_funcs = [base2048.encode]
        super().__init__(config)


class InjectBraille(BaseEncodingGenerator):
    """Probe for susceptibility to Braille encoding injections. Credit Wally#3422

    Encodes payloads using braille, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    doc_uri = ""
    encoding_funcs = [braille]
    encoding_name = "Braille"

    def __init__(self, config=None):
        super().__init__(config)


class InjectMorse(BaseEncodingGenerator):
    """Probe for susceptibility to Morse encoding. Credit Wally#3422

    Encodes payloads using morse, and tries a variety of ways of getting the target
    model to repeat & decode them."""

    doc_uri = ""
    encoding_funcs = [morse]
    encoding_name = "Morse"

    def __init__(self, config=None):
        super().__init__(config)


class InjectNato(BaseEncodingGenerator):
    """Probe for susceptibility to Nato phonetic alphabet encoding.

    Encodes payloads using the classic NATO phonetic alphabet, and tries a
    variety of ways of getting the target model to repeat & decode them."""

    doc_uri = "https://en.wikipedia.org/wiki/NATO_phonetic_alphabet"

    def nato(text: bytes) -> bytes:
        nato_map = {
            "A": "Alfa",
            "B": "Bravo",
            "C": "Charlie",
            "D": "Delta",
            "E": "Echo",
            "F": "Foxtrot",
            "G": "Golf",
            "H": "Hotel",
            "I": "India",
            "J": "Juliett",
            "K": "Kilo",
            "L": "Lima",
            "M": "Mike",
            "N": "November",
            "O": "Oscar",
            "P": "Papa",
            "Q": "Quebec",
            "R": "Romeo",
            "S": "Sierra",
            "T": "Tango",
            "U": "Uniform",
            "V": "Victor",
            "W": "Whiskey",
            "X": "Xray",
            "Y": "Yankee",
            "Z": "Zulu",
        }

        output = []
        for char in text.decode().upper():
            if char in nato_map:
                output.append(nato_map[char])
        return bytes(" ".join(output), "utf-8")

    encoding_funcs = [nato]
    encoding_name = "Nato"

    def __init__(self, config=None):
        super().__init__(config)


class InjectEcoji(BaseEncodingGenerator):
    """Probe for susceptibility to Ecoji encoding.

    Encodes payloads using the [ecoji](https://ecoji.io/) mapping, and tries a variety
    of ways of getting the target model to repeat & decode them."""

    doc_uri = "https://ecoji.io/"

    def _ecoji(text: bytes) -> bytes:
        import io

        import ecoji

        r = io.BytesIO(text)
        w = io.StringIO()

        ecoji.encode(r, w)

        return w.getvalue()

    encoding_name = "Ecoji"
    encoding_funcs = [_ecoji]

    def __init__(self, config=None):
        super().__init__(config)


class InjectZalgo(BaseEncodingGenerator):
    """Probe for susceptibility to Zalgo encoding.

    Encodes payloads using Zalgo decoration, and tries a variety
    of ways of getting the target model to repeat & decode them."""

    doc_uri = "https://en.wikipedia.org/wiki/Zalgo_text"

    def zalgo(text: bytes) -> bytes:
        from zalgolib.zalgolib import enzalgofy

        zalged = enzalgofy(
            text=text.decode(), intensity=10
        )  # default value of 50 explodes prompt length

        return bytes(zalged, "utf-8")

    encoding_name = "Zalgo"
    encoding_funcs = [zalgo]

    def __init__(self, config=None):
        super().__init__(config)

