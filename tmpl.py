import sys
import os
import openai

openai.api_key = open(".OPENAI_API_KEY").read().rstrip('\n')

import json

def chat_call(msgs, funcs):
    print(funcs[0]["name"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[msgs],
        functions=funcs,
        function_call="auto"
    )
    print("received response:")
    print(response)
    return response

#def save_template_data(template, data):

def usr(msg):
    return { "role": "user", "content": msg }

def fn_res(name, res):
    return {"role": "function", "name": name, "content": res }

def sys(msg):
    return { "role": "system", "content": msg }

def found_template_data(p):
   os.makedirs(f"templates/{p.partial_name}", exist_ok=True)
   os.makedirs(f"data/{p.partial_name}", exist_ok=True)
   print(f"saving partial {p.partial_name}") 
   with open(f"templates/{p.partial_name}","w") as f: f.write(p.template)
   with open(f"data/{p.partial_name}","w") as f: f.write(p.template_data)


def extract_template(msgs, filename):
  found_template_data = {
                "name": "found_template_data",
                "description": "Save a section of disentangled mustache template and JSON data extracted from HTML provided by the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "partial_name": {
                            "type": "string",
                            "description": "Name of the mustache partial for the section extracted, such as header, footer, features, etc."
                        },
                        "template": {
                            "type": "string",
                            "description": "A mustache partial for the page section. Remove text or image literals and replace with semantic variable names etc. according to normal mustache.js usage. IMPORTANT: For header, make sure to include full page start elements such as html, head etc. and nav so it can be used to start a working html file on each page.",
                        },
                        "template_data": {
                            "type": "string", "description": "JSON representing data that when injected into the header template will recreate the original HTML for that section."},
                    },
                    "required": ["partial_name", "template", "template_data"],
                },
            }
  if filename is not None:
      html = open(filename, 'r').read()
      prompt = usr(f"Examine the following HTML and convert to mustache template partials using multiple calls to the function described. Should have header, footer, and at least one partial for the body depending on the best logical decomposition.\n{html}")
  else:
      prompt = usr(f"Convert any remaining sections.")
  system = sys("You are an experienced AI front-end engineer.")
  response = chat_call(system+msgs+prompt, [found_template_data])
  message = response["choices"][0]["message"]
  print(message)
  if message.get("function_call"):
      func_resp = found_template_data(message.get("partial_name"),
                                      message.get("template"),
                                      message.get("template_data"))

      msgs += fn_res("found_template_data", func_resp)
      extract_template(msgs) 


extract_template([], sys.argv[1])


