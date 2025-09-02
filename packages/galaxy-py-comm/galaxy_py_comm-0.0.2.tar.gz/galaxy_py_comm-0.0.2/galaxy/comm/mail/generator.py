#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class MailCSSGenerator(object):
    """
    classdocs
    """

    @staticmethod
    def generate() -> str:
        css = """
p.Normal, li.Normal, div.Normal {
  margin: 0cm;
  font-size: 10.0pt;
  font-family: "Arial", sans-serif;
  color: black
  mso-ligatures: standardcontextual;
  mso-fareast-language: EN-US;
}

a:link, span.Hyperlink {
  mso-style-priority: 99;
  color: #467886;
  text-decoration: underline;
}

@page Section1 {
  size: 612.0pt 792.0pt;
  margin: 72.0pt 72.0pt 72.0pt 72.0pt;
}

div.Section1 {
  page: Section1;
}

"""
        return css


class MailHTMLBodyContentGenerator(object):
    """
    classdocs
    """

    @staticmethod
    def generate() -> str:
        html = """
<body lang=EN-GB style='word-wrap:break-word'>
    <div class=Section1>
        <p class=Normal>Hi Font Office Team,</p>
        <p class=Normal>&nbsp;</p>
        <p class=Normal>Please find the report in attachment.</p>
        <p class=Normal>&nbsp;</p>
        <p class=Normal>Contact Bastien Saltel (<a href="mailto:bastien.saltel@sucfin.com">bastien.saltel@sucfin.com</a>) for any issue.</p>
        <p class=Normal>&nbsp;</p>
    </div>
</body>
"""
        return html


class MailHTMLContentGenerator(object):
    """
    classdocs
    """

    @staticmethod
    def generate() -> str:
        html = """
<!DOCTYPE html>
<html>
<head>
    <style>{}</style>
</head>
{}
</html>
""".format(MailCSSGenerator.generate(), MailHTMLBodyContentGenerator.generate())
        return html
