"""This module creates several person objects, and pickles them."""

import pickle
import person_class

def main():
    """pickling the following information in personobjects"""
    real_names = ["guest"]
    authorized_mails = ["guest.hjg6@gmail.com"]
    nicknames = ["Loyal servant"]
    authorized_user_list = []

    for real_name, mail, nickname in zip(real_names, authorized_mails, nicknames):
        authorized_user = person_class.Person(real_name, mail, nickname)
        authorized_user_list.append(authorized_user)

    with open('pickled_users.pickle', 'wb') as picklefile:
        pickle.dump(authorized_user_list, picklefile)

if __name__ == "__main__":
    main()
