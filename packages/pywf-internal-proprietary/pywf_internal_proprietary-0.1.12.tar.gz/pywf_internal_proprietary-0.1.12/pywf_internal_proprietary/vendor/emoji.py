# -*- coding: utf-8 -*-

"""
Enumerate useful, UTF8 emoji characters.

Full list is here: https://unicode.org/emoji/charts/full-emoji-list.html

Usage example:

.. code-block:: python

    from emoji import Emoji
"""

__version__ = "0.1.1"


class Emoji:
    start_timer = "⏱"
    end_timer = "⏰"
    start = "⏯"
    end = "⏹"
    error = "🔥"

    relax = "🌴"

    doc = "📔"
    test = "🧪"
    install = "💾"
    build = "🪜"
    deploy = "🚀"
    delete = "🗑"
    config = "🔯"
    tada = "🎉"

    cloudformation = "🐑"
    awslambda = "λ"
    s3 = "🪣"

    template = "📋"
    computer = "💻"
    package = "📦"
    email = "📫"
    factory = "🏭"
    no_entry = "🚫"
    warning = "❗"
    label = "🏷"

    thumb_up = "👍"
    thumb_down = "👎"
    attention = "👉"

    happy_face = "😀"
    hot_face = "🥵"
    anger = "💢"
    eye = "👀"

    red_circle = "🔴"
    green_circle = "🟢"
    yellow_circle = "🟡"
    blue_circle = "🔵"

    red_square = "🟥"
    green_square = "🟩"
    yellow_square = "🟨"
    blue_square = "🟦"

    succeeded = "✅"
    failed = "❌"

    arrow_up = "⬆"
    arrow_down = "⬇"
    arrow_left = "⬅"
    arrow_right = "➡"

    python = "🐍"

    sbx = "📦"
    tst = "🧪"
    prd = "🏭"

    install_phase = "🌱"
    pre_build_phase = "🌿"
    build_phase = "🍀"
    post_build_phase = "🌲"


if __name__ == "__main__":
    chars = list()
    for k, v in Emoji.__dict__.items():
        if not k.startswith("_"):
            if len(v) != 1:
                print(f"{k} = {v}, len = {len(v)}")

            # if len(v) == 1:
            chars.append(v)

    print(" ".join(chars))
