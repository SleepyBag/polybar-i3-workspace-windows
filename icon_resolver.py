import collections
import re
import pickle


class Rule:
    prop = ''
    expression = ''
    value = ''
    color = ''

    def __init__(self, prop: str, expression: str, value: str, color: str):
        self.prop = prop
        self.expression = expression
        self.value = value
        self.color = color


    def match(self, data: dict) -> bool:
        return re.match(self.expression, data[self.prop]) != None


class IconResolver:
    _rules = []
    _cache = {}


    def __init__(self, rules):
        self._rules = [self._parse_rule(rule) for rule in rules]

    def get_color(self, app):

        for rule in self._rules:
            if rule.match(app):
                return rule.color


    def resolve(self, app):
        out = app['class'][0]
        id = pickle.dumps(app)

        if id in self._cache:
            return self._cache[id]

        for rule in self._rules:
            if rule.match(app):
                out = '%{F' + rule.color + '}' + rule.value + '%{F-}'
                break

        self._cache[id] = out

        return out


    def _parse_rule(self, rule) -> Rule:
        parts = rule[0].split('=', 1)

        prop = 'class'
        match = ''

        if len(parts) > 1:
            prop = parts[0]
            match = parts[1]
        else:
            match = parts[0]

        #  exp = re.escape(match).replace('\\*', '.+')
        exp = match

        return Rule(prop, exp, rule[1], rule[2])
