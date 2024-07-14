import g4f
import discord

prompt = input('ur question:')

response = g4f.ChatCompletion.create(
    model=g4f.models.default,
    provider=g4f.Provider.Koala,
    messages=[
        {"role": "system", "content": "Answer only with emojis"},
        {"role": "user", "content": prompt},   
    ]
) 


print(f'gpt: {response}')