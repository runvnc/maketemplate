import sys
import os
import openai
import json

openai.api_key = open(".OPENAI_API_KEY").read().rstrip('\n')

import json

def chat_call(msgs, funcs):
    print(funcs[0]["name"])
    print(msgs)
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
    return {"role": "function", "name": name, "content": json.dumps(res) }

def sysmsg(msg):
    return { "role": "system", "content": msg }

def found_template_data(partial_name, template, data):
   os.makedirs(f"templates", exist_ok=True)
   os.makedirs(f"data", exist_ok=True)
   print(f"saving partial {partial_name}") 
   with open(f"templates/{partial_name}","w") as f: f.write(template)
   with open(f"data/{partial_name}.json","w") as f: f.write(json.dumps(data))
   return json.dumps({"result": "success", 
                      "output_files": [ f"templates/{partial_name}",
                                        f"data/{partial_name}.json"]})

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
                    "data": {
                        "type": "object", "description": "Object with properties that when injected into the template will recreate the original HTML for that section. Some properties may contain arrays. Use the data as much as possible instead of including literal text, for anything that is repeating or is likely to need to be edited.",
                        "properties": {},
                        "additionalProperties": True},
                    "template": {
                        "type": "string",
                        "description": "A mustache partial for the page section. Remove text or image literals and replace with semantic data names etc. according to normal mustache.js usage. IMPORTANT: For header, make sure to include full page start elements such as doctype, HTML, HEAD etc. so that it will suffice for valid html at the top of the file. \n CRITICAL: Also use mustache sections and data for repeating items like lists such as nav items rather than including them literally e.g\n{{#somelist}}\n  <li>{{item}}</li>\n{{/somelist}}.",
                    },
               },
                "required": ["partial_name", "data", "template"],
            },
        }

def extract_template(msgs, filename):
  if filename is not None:
      html = open(filename, 'r').read()
      prompt = usr(f"Examine the following HTML and convert to mustache template partials with extracted fields rather than literal text, using calls to the function described. Should have header, footer, and at least one partial for the body depending on the best logical decomposition. The header partial must include starting tags like doctype, html, nav (or equivalent) etc. and footer must include closing html tag, since those partials will be used to wrap the final html which must be valid.\n\n{html}")
  else:
      prompt = usr(f"Convert the next remainin section, if any (see message above with HTML).")
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
                                      obj.get("template"),
                                      obj.get("data"))

      msgs += [prompt, fn_res("found_template_data", func_resp)]
      return extract_template(msgs, None) 
  else:
      print("Done.")

extract_template([], sys.argv[1])


