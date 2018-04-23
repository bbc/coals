#!/usr/bin/python3
#
# Copyright 2018 British Broadcasting Corporation
#
# Author: Michael Sparks <michael.sparks@bbc.co.uk>
#
# All Rights Reserved
#

import pprint
import os

import als_core
from als_core import Debug, initialise_system, banner, infer_concepts_and_ngram_deltas, infer_conceptual_dependencies
from als_core import find_resources_for_user, filter_secure_resources, ask_user_to_choose_resource, present_resource
from als_core import update_user_for_resource, concept_ids, resource_ids

world = initialise_system()

Debug(pprint.pformat(world.__json__(),width=300))

user = {}
user["resources_done"] = []
user["extension"] = None
user["ngrams"] = {}

done = False    
banner("User model",user)


Debug(world.get("Concept"))
Debug(world.get("Resource"))

banner("All Concepts:",", ".join( concept_ids(world) ))
banner("All resources:",", ".join( resource_ids(world) ))

infer_concepts_and_ngram_deltas()
infer_conceptual_dependencies()

while not done:

    candidates = find_resources_for_user(world.get("Resource"), user)
    candidates, optional = filter_secure_resources(candidates, user)
    if len(optional) > 0:
        if user["extension"] == None:
            print("There are optional tutorials right now")
            print("Do you want to do them?")
            x = input("yes (this once), no (this once), always, never, later> ")
            if x.lower().startswith("y"):
                candidates = optional
            elif x.lower().startswith("a"):
                user["extension"] = "always"
            elif x.lower().startswith("never"):
                user["extension"] = "never"
            elif x.lower().startswith("l"):
                user["extension"] = "later"

        if user["extension"] == "always":
            candidates = optional

    if len(candidates) == 0:
        if len(optional)>0:
            if user["extension"] != "never":
                print()
                print("No mainline/candidate tutorials left -- only optional ones")
                print("Do you want to do them?")
                x = input("yes (this once), no (this once), always, never, later> ")
                if x.lower().startswith("y"):
                    candidates = optional
                elif x.lower().startswith("a"):
                    user["extension"] = "always"
                elif x.lower().startswith("never"):
                    user["extension"] = "never"
                elif x.lower().startswith("l"):
                    user["extension"] = "later"

            if user["extension"] == "always":
                candidates = optional

    if len(candidates) == 0:
        done = True
        continue

    Debug("-------------\n", candidates)
    banner("Candidate resources for you to do", [ x.get_component("Resource").logical_id for x in candidates ])
    print()

    resource = ask_user_to_choose_resource(candidates)

    present_resource(resource)
    input("press return when done\n")

    update_user_for_resource(user,resource)

    banner("User model",user)
    print()

print()
print("You're done!")
print()
banner("Final User model",user)

world.store_state()

