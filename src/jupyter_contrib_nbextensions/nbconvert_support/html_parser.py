"""Simple HTML Parser with transform functionality"""

from html.parser import HTMLParser


class TagTransform:
    """
    Abstract class for a tag transformation rule.
    """
    def __init__(self, name, tags):
        """
        Args:
        name (str): The name of the transformation.
        tags (list of str): Tag names for which this transform applies.
        """
        self._name = name
        self._tags = tags

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags

    def transform(self, attrs):
        """ Do the transformation on the tag.
            Args:
            attrs (dict of (key,value)): Dict of (attribute, value) pairs
        """
        pass


class HTMLTransformer(HTMLParser):
    """
    A simple HTML parser which supports transforming tags by registering
    transformation rules on to a stack of rules.
    """

    def __init__(self):
        # We dont want char references to be converted,
        # modify HTML as little as possible!
        super(HTMLTransformer, self).__init__(convert_charrefs=False)
        self.tagTransforms = {}

    def fromstring(self, str):
        self.feed(str)

    def get_html(self):
        return self.htmlString

    def pushTagTransform(self, tagTransform):
        for tag in tagTransform.get_tags():
            if tag not in self.tagTransforms:
                queue = self.tagTransforms[tag] = []
            else:
                queue = self.tagTransforms[tag]

            queue.append(tagTransform)

    def reset(self):
        super(HTMLTransformer, self).reset()
        self.htmlString = ""

    def handle_starttag(self, tag, attrs):
        self.htmlString += "<" + tag
        self.transformTag(tag, attrs)
        self.htmlString += ">"

    def handle_endtag(self, tag):
        self.htmlString += "</" + tag + ">"

    def handle_startendtag(self, tag, attrs):
        self.htmlString += "<" + tag
        self.transformTag(tag, attrs)
        self.htmlString += "/>"

    def transformTag(self, tag, attrs):
        if tag in self.tagTransforms:
            attrsOut = dict(attrs)
            for tr in self.tagTransforms[tag]:
                tr.transform(attrsOut)

            self.htmlString += "".join([
                ' %s="%s"' % (k, v) for k, v in attrsOut.items()])
        else:
            self.htmlString += "".join([
                ' %s="%s"' % (k, v) for k, v in attrs])

    def handle_data(self, data):
        self.htmlString += data

    def handle_entityref(self, name):
        self.htmlString += "&" + name + ";"

    def handle_charref(self, name):
        self.htmlString += "&#" + name + ";"

    def handle_comment(self, comment):
        self.htmlString += "<!--" + comment + "-->"

    def handle_decl(self, decl):
        self.htmlString += "<!" + decl + ">"

    def handle_pi(self, proc):
        self.htmlString += "<?" + proc + ">"

    def unknown_decl(self, unknown):
        self.htmlString += "<![" + unknown + "]>"
