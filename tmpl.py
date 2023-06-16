import sys
import os
import openai
import json

openai.api_key = open(".OPENAI_API_KEY").read().rstrip('\n')

import json

def chat_call(msgs, funcs):
    print(funcs[0]["name"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=msgs,
        temperature=0,
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

def sysmsg(msg):
    return { "role": "system", "content": msg }

def found_template_data(partial_name, template, data):
   os.makedirs(f"templates", exist_ok=True)
   os.makedirs(f"data", exist_ok=True)
   print(f"saving partial {partial_name}") 
   with open(f"templates/{partial_name}","w") as f: f.write(template)
   with open(f"data/{partial_name}.json","w") as f: f.write(json.dumps(data))

def_found_template_data = {
            "name": "found_template_data",
            "description": "Save a section of disentangled mustache template and JSON data extracted from HTML provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partial_name": {
                        "type": "string",
                        "description": "Name of the mustache partial for the section extracted, such as header, footer, features, testimonials, etc."
                    },
                    "template": {
                        "type": "string",
                        "description": "A mustache partial for the page section. Remove text or image literals and replace with semantic variable names etc. according to normal mustache.js usage. IMPORTANT: For header, make sure to include full page start elements such as html, head etc. and nav. Use appropriate mustache constructs and data for repeating items like lists.",
                    },
                    "data": {
                        "type": "object", "description": "Object with properties that when injected into the template will recreate the original HTML for that section."},
                },
                "required": ["partial_name", "data", "template"],
            },
        }

def extract_template(msgs, filename):
  if filename is not None:
      html = open(filename, 'r').read()
      prompt = usr(f"Examine the following HTML and convert to mustache template partials using multiple calls to the function described. Should have header, footer, and at least one partial for the body depending on the best logical decomposition.\n{html}")
  else:
      prompt = usr(f"Convert any remaining sections.")
  system = sysmsg("You are an experienced AI front-end engineer.")
  response = chat_call([system]+msgs+[prompt], [def_found_template_data])
  message = response["choices"][0]["message"]
  print(message)
  if message.get("function_call"):
      args = message.get("function_call").get("arguments")
      print("args:")
      print(args)
      obj = json.loads(args)
      func_resp = found_template_data(obj.get("partial_name"),
                                      obj.get("partial_template"),
                                      obj.get("data"))

      msgs += fn_res("found_template_data", func_resp)
      return extract_template(msgs) 
  else:
      print("Done.")

extract_template([], sys.argv[1])


