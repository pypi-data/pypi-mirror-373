__all__ = ["SplitText"]

import re


class SplitText:
    def __init__(self):
        self.rv = []
        self.split_pos = []
        self.pos = -1
        self.current = ""
        self.in_quote = False

    def seek(self, delta):
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                self.pos -= 1
                self.current = self.current[:-1]
            else:
                self.pos += 1
                self.current += self.text[self.pos]
            if self.text[self.pos] in '"“”':
                self.in_quote = not self.in_quote
        return self.text[self.pos]

    def peek(self, delta):
        p = self.pos + delta
        return self.text[p] if p < self.end_pos and p >= 0 else ""

    def commit(self):
        self.rv.append(self.current)
        self.current = ""
        self.split_pos = []

    def __call__(
        self,
        text: str,
        desired_length: int = 100,
        max_length: int = 200,
    ) -> list[str]:
        self.text = text
        self.end_pos = len(self.text) - 1
        self.max_length = max_length
        self.desired_length = desired_length
        while self.pos < self.end_pos:
            c = self.seek(1)
            if len(self.current) >= self.max_length:
                if len(self.split_pos) > 0 and len(self.current) > (
                    self.desired_length / 2
                ):
                    d = self.pos - self.split_pos[-1]
                    self.seek(-d)
                else:
                    while (
                        c not in "!?.\n "
                        and self.pos > 0
                        and len(self.current) > self.desired_length
                    ):
                        c = self.seek(-1)
                self.commit()
            elif not self.in_quote and (
                c in "!?\n" or (c == "." and self.peek(1) in "\n ")
            ):
                while (
                    self.pos < len(self.text) - 1
                    and len(self.current) < self.max_length
                    and self.peek(1) in "!?."
                ):
                    c = self.seek(1)
                self.split_pos.append(self.pos)
                if len(self.current) >= self.desired_length:
                    self.commit()
            elif self.in_quote and self.peek(1) == '"“”' and self.peek(2) in "\n ":
                self.seek(2)
                self.split_pos.append(self.pos)
        self.rv.append(self.current)
        self.rv = [s.strip() for s in self.rv]
        self.rv = [
            s for s in self.rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)
        ]

        return self.rv
