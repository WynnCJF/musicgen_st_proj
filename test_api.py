import replicate

output = replicate.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input={
        "model_version": "melody",
        "prompt": "electric guitar solo, shoegaze, clean and clear recording quality, perfect for music production",
        "duration": 15,
    }
)

print(output)