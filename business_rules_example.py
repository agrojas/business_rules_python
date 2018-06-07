import datetime

from business_rules import run_all
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC
from business_rules.variables import (BaseVariables,
                                      numeric_rule_variable,
                                      string_rule_variable)


class User:
    def __init__(self, user_name, followers, zone):
        self.user_name = user_name
        self.followers = followers
        self.zone = zone

    def __repr__(self):
        return '<User(user_name={self.user_name!r},followers={self.followers!r},zone={self.zone!r})>'.format(self=self)


class History:
    def __init__(self, user, likes, dislikes, views):
        self.user = user
        self.likes = likes
        self.dislikes = dislikes
        self.views = views
        self.date_time = datetime.datetime.now()
        self.score = 10  # default

    def __repr__(self):
        return '<History(user={self.user!r},date_time={self.date_time!r},likes={self.likes!r},dislikes={self.dislikes!r},views={self.views!r},score={self.score!r})>'.format(
            self=self)


    def set_score(self, score):
        # Validar el score
        self.score = score


class HistoryVariables(BaseVariables):

    def __init__(self, history):
        self.history = history

    @numeric_rule_variable()
    def views(self):
        return self.history.views

    @numeric_rule_variable()
    def likes(self):
        return self.history.likes

    @numeric_rule_variable(label='Days until expiration')
    def expiration_days(self):
        return (self.history.date_time.date - datetime.date.today()).days

    @numeric_rule_variable()
    def dislikes(self):
        return self.history.dislikes

    @numeric_rule_variable()
    def like_rate(self):
        return (self.history.likes / (self.history.dislikes + self.history.likes))

    @string_rule_variable()
    def user_zone(self):
        return self.history.user.zone

    @numeric_rule_variable()
    def user_followers(self):
        return self.history.user.followers


class HistoryActions(BaseActions):

    def __init__(self, history):
        self.history = history

    @rule_action(params={"score": FIELD_NUMERIC})
    def top_score(self, score):
        print("top_score---> {}".format(score))
        calculated_score = self.history.score + 0.5 * score
        self.history.set_score(calculated_score)

    @rule_action(params={"bonus": FIELD_NUMERIC})
    def apply_bonus(self, bonus):
        print("apply_bonus---> {}".format(bonus))
        calculated_score = self.history.score + 0.1 * bonus
        self.history.set_score(calculated_score)

    @rule_action(params={"penalty": FIELD_NUMERIC})
    def apply_penalty(self, penalty):
        print("apply_penalty ---> {}".format(penalty))
        calculated_score = self.history.score - 0.1 * penalty
        self.history.set_score(calculated_score)


rules = [
    # likes < 5 AND views < 20
    {"conditions": {"all": [
        {"name": "likes",
         "operator": "less_than",
         "value": 5
         },
        {"name": "views",
         "operator": "less_than",
         "value": 20
         }
    ]},
        "actions": [
            {"name": "apply_penalty",
             "params": {"penalty": 10}
             }
        ]
    },
    # views > 20
    {"conditions": {"all": [
        {"name": "views",
         "operator": "greater_than",
         "value": 20
         },
         {"name": "likes",
         "operator": "greater_than",
         "value": 20
         }
         ,
         {"name": "dislikes",
         "operator": "less_than",
         "value": 10
         }
    ]},
        "actions": [
            {"name": "apply_bonus",
             "params": {"bonus": 10}
             }
        ]
    }

]

if __name__ == '__main__':
    # Creo las historias
    user_1 = User("user_name_1", 100, "AR")
    user_2 = User("user_name_2", 10, "BR")
    user_3 = User("user_name_3", 10000, "AR")
    history_1 = History(user_1, 1, 0, 10)
    history_2 = History(user_2, 10, 0, 1000)
    history_3 = History(user_3, 100, 5, 1000)

    histories = [history_1, history_2, history_3]
    # Aplico las reglas
    for history in histories:
        run_all(rule_list=rules,
                defined_variables=HistoryVariables(history),
                defined_actions=HistoryActions(history),
                stop_on_first_trigger=True
                )
    # Imprimo resultados luego de aplicar las reglas
    for history in histories:
        print(history)
