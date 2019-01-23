# Compromised, MIT Mystery Hunt 2019
# https://molasses.holiday/puzzle/compromised
# Solution to the logic constraint puzzle part using CSP

# Runs in about 3 minutes, and results in 4 solutions. The only differences between the solutions
# are whether Demetrius and Isabelle have participated in a joint mission. Apparently that's
# unconstrained. But I think it narrows things down enough to match them up by hand.

# A QUAD COLLEGE LIVENEAR LSOLITAIRE DOFFICE SMARTIAL
# B ARMY MILITARY JOINT LWHITTLE DHEELS SLIPS
# C ARMY MILITARY JOINT LVERB DRATS STANGO
# D QUAD ARMY MILITARY [JOINT] LIVENEAR LXWORD DCAM SSURVIVE
# E QUAD COLLEGE LIVENEAR LFACTOR DEAT SACROBAT
# F NAVY MILITARY JOINT LPOETRY DLATE SCOPTER
# G NAVY MILITARY JOINT LSWIPE DSEAT SNIGHT
# H NAVY MILITARY JOINT LPARTY DGRATES SCOVERT
# I QUAD ARMY MILITARY [JOINT] LCALL DBATTERY SLOCK
# J QUAD COLLEGE LBIRD DPOCKET STECH



# Uses python-constraint library:
# sudo pip3 install python-constraint

from constraint import *

# Convention: use uppercase for VARIABLE NAMES, lowercase for values those variables can take.

# Spies are referred by letter A-J when used in a variable name, or number 0-9 when used in a
# variable value.
SPY_NAMES = "ABCDEFGHIJ"
spy_indexes = list(range(len(SPY_NAMES)))

problem = Problem()

# VARIABLES

# Define "feature" as something that may apply to any number of spies.
# These variables get assigned a value True or False if the corresponding spy has that feature,
# e.g. COLLEGEF is True if Fitzgerald went to college.
FEATURES = [
	"QUAD",  # eats outside in the quad.
	"COLLEGE",  # completed college.
	"ARMY",  # was in the Army.
	"NAVY",  # was in the Navy.
	"MILITARY",  # was in the military.
	"JOINT",  # has participated in a joint mission.
	"LIVENEAR",  # lives near other spies.
]

# Define "trait" as something we assume applies to exactly one spy, i.e. professional skill, like,
# and dislike.
# These variables get assigned a value 0-9 corresponding to the spy that has the trait, e.g.
# SNIGHT = 1 if Broderick has excellent night vision.
TRAITS = (
	"LFACTOR LSWIPE LCALL LVERB LWHITTLE LBIRD LPOETRY LSOLITAIRE LXWORD LPARTY "
	"DEAT DRATS DOFFICE DCAM DHEELS DLATE DSEAT DBATTERY DPOCKET DGRATES "
	"STECH SLIPS SCOPTER SLOCK SSURVIVE STANGO SNIGHT SCOVERT SACROBAT SMARTIAL"
).split()

# Every (FEATURE, SPY) pair must be True or False
FEATURE_VARS = [FEATURE + SPY for FEATURE in FEATURES for SPY in SPY_NAMES]
problem.addVariables(FEATURE_VARS, [False, True])
# Every trait must apply to one of the spies.
problem.addVariables(TRAITS, spy_indexes)



# CONSTRAINTS

# We'll assume we can assign all the features and traits just using the 19 givens, not using any
# information from the matchmaking profiles.

# For the purpose of these functions, SPY is a string either referring to a spy by the first
# letter of their name (e.g. "C" for Christopher), or naming a trait, in which case it refers to the
# spy with that trait (e.g. "LBIRD" for the spy that enjoys birdwatching).

def split_spies(SPIES):
	SPIES_BY_NAME = [SPY for SPY in SPIES if SPY in SPY_NAMES]
	SPIES_BY_TRAIT = [SPY for SPY in SPIES if SPY not in SPY_NAMES]
	assert all(SPY in TRAITS for SPY in SPIES_BY_TRAIT)
	return SPIES_BY_NAME, SPIES_BY_TRAIT

# Enforce that the given spies are all different.
def different(*SPIES):
	SPIES_BY_NAME, SPIES_BY_TRAIT = split_spies(SPIES)
	# Each of the given traits are not assigned to any of the given named spies.
	if SPIES_BY_NAME and SPIES_BY_TRAIT:
		indexes = [SPY_NAMES.index(SPY) for SPY in SPIES_BY_NAME]
		problem.addConstraint(NotInSetConstraint(indexes), SPIES_BY_TRAIT)
	# Each of the given traits gets assigned to a different spy.
	if len(SPIES_BY_TRAIT) > 1:
		problem.addConstraint(AllDifferentConstraint(), SPIES_BY_TRAIT)

# Enforce that the given spies are all the same.
def same(*SPIES):
	SPIES_BY_NAME, SPIES_BY_TRAIT = split_spies(SPIES)
	assert len(SPIES_BY_NAME) <= 1
	if SPIES_BY_NAME and SPIES_BY_TRAIT:
		index = SPY_NAMES.index(SPIES_BY_NAME[0])
		problem.addConstraint(InSetConstraint([index]), SPIES_BY_TRAIT)
	# Each of the given traits gets assigned to a different spy.
	if len(SPIES_BY_TRAIT) > 1:
		problem.addConstraint(AllEqualConstraint(), SPIES_BY_TRAIT)

# Enforce that the given spies have (or don't have) the given feature.
# Also enforce that the given spies are all different.
def has_feature(FEATURE, *SPIES, has=True):
	different(*SPIES)
	SPIES_BY_NAME, SPIES_BY_TRAIT = split_spies(SPIES)
	# Each of the given traits are not assigned to any of the given named spies.
	if SPIES_BY_NAME:
		FEATURES = [FEATURE + SPY for SPY in SPIES_BY_NAME]
		problem.addConstraint(InSetConstraint([has]), FEATURES)
	if SPIES_BY_TRAIT:
		def valid(spy_index, *features):
			return features[spy_index] == has
		FEATURES = [FEATURE + SPY for SPY in SPY_NAMES]
		for SPY_INDEX in SPIES_BY_TRAIT:
			problem.addConstraint(FunctionConstraint(valid), [SPY_INDEX] + FEATURES)

# Given a predicate that takes a list of feature values, enforce that the given spies
def feature_predicate(predicate, FEATURE, *SPIES):
	different(*SPIES)
	SPIES_BY_NAME, SPIES_BY_TRAIT = split_spies(SPIES)
	FEATURES = [FEATURE + SPY for SPY in SPY_NAMES]
	ntraits = len(SPIES_BY_TRAIT)
	named_indexes = [SPY_NAMES.index(SPY_NAME) for SPY_NAME in SPIES_BY_NAME]
	def valid(*values):
		# Exctract the binary feature vector corresponding to the given spies.
		trait_indexes = values[:ntraits]
		indexes = named_indexes + list(trait_indexes)
		features = values[ntraits:]
		fvalues = [features[index] for index in indexes]
		return predicate(fvalues)
	problem.addConstraint(FunctionConstraint(valid), SPIES_BY_TRAIT + FEATURES)	

# Enforce that the given spies have the same value for the given feature.
def same_feature(FEATURE, *SPIES):
	all_same = lambda features: all(features) or not any(features)  # i.e. all True or all False.
	feature_predicate(all_same, FEATURE, *SPIES)

# Enforce that the given spies have the different values for the given feature (obviously, since
# features can only be True or False, this will only work with two spies given).
def different_feature(FEATURE, *SPIES):
	all_different = lambda features: all(features.count(f) == 1 for f in features)
	feature_predicate(all_different, FEATURE, *SPIES)

# Enforce that the given number of the given spies have the same value for the given feature.
def feature_count(FEATURE, n, *SPIES):
	total_count = lambda features: features.count(True) == n
	feature_predicate(total_count, FEATURE, *SPIES)


# Assume each spy can have exactly one like, one dislike, and ane skill.
problem.addConstraint(AllDifferentConstraint(), [TRAIT for TRAIT in TRAITS if TRAIT.startswith("L")])
problem.addConstraint(AllDifferentConstraint(), [TRAIT for TRAIT in TRAITS if TRAIT.startswith("D")])
problem.addConstraint(AllDifferentConstraint(), [TRAIT for TRAIT in TRAITS if TRAIT.startswith("S")])

# The Army and Navy both count as the military, i.e. any spy in the Army must also be in the military.
imp = lambda x, y: not x or y
for BRANCH in ["ARMY", "NAVY"]:
	for SPY in SPY_NAMES:
		problem.addConstraint(FunctionConstraint(imp), [BRANCH + SPY, "MILITARY" + SPY])

# 1. The spy who enjoys solving crossword puzzles always eats lunch outside in the quad, together
# with the technology specialist, the spy who hates those annoying people who eat and drive,
# Alexandria, and Isabelle.
has_feature("QUAD", "LXWORD", "STECH", "DEAT", "A", "I")

# 2. Harriette and Gwendolyn were once part of a joint mission with the spy who enjoys writing
# poetry, the spy who reads lips, and the spy who hates it when there are rats in the air vents.
# Now the five of them always eat lunch together in the cafeteria.
has_feature("JOINT", "H", "G", "LPOETRY", "SLIPS", "DRATS")
has_feature("QUAD", "H", "G", "LPOETRY", "SLIPS", "DRATS", has=False)

# 3. Three of the spies—the spy who enjoys factoring large numbers in their head, the spy who hates
# it when Microsoft Office freezes, and Jefferson—went to college together, but none of them has
# ever served in the military or participated in a joint mission.
has_feature("COLLEGE", "LFACTOR", "DOFFICE", "J")
has_feature("MILITARY", "LFACTOR", "DOFFICE", "J", has=False)
has_feature("JOINT", "LFACTOR", "DOFFICE", "J", has=False)

# 4. The spy who enjoys swiping left on dating profiles, the spy who flies helicopters, and
# Harriette all enlisted in the Navy after high school and didn’t go to college.
has_feature("NAVY", "LSWIPE", "SCOPTER", "H")
has_feature("COLLEGE", "LSWIPE", "SCOPTER", "H", has=False)

# 5. Four of the spies—Christopher, Demetrius (who doesn’t know how to pick locks), the lip reader,
# and the spy who enjoys obsessively calling HQ every five minutes—all enlisted in the Army after
# high school and also never went to college. Two of them eat lunch in the quad and two in the
# cafeteria.
different("D", "SLOCK")
has_feature("ARMY", "C", "D", "SLIPS", "LCALL")
has_feature("COLLEGE", "C", "D", "SLIPS", "LCALL", has=False)
feature_count("QUAD", 2, "C", "D", "SLIPS", "LCALL")

# 6. The spy who hates faulty hidden cameras also has awesome survival skills. They eat lunch with
# the lock-picking specialist.
same("DCAM", "SSURVIVE")
same_feature("QUAD", "DCAM", "SLOCK")

# 7. The spy whose special mission skill is undercover tango dancing (and who served in the Army
# after high school) enjoys conjugating verbs.
same("STANGO", "LVERB")
has_feature("ARMY", "STANGO")

# 8. The spy who enjoys whittling small animal figurines also hates wearing heels that make noise
# when you walk.
same("LWHITTLE", "DHEELS")

# 9. Fitzgerald, who is not the lip reader or the spy with superior night vision, hates those
# annoying partners who are late to the drop.
different("F", "SLIPS")
different("F", "SNIGHT")
same("F", "DLATE")

# 10. Jefferson, who is not annoyed by people who eat and drive, enjoys birdwatching.
different("J", "DEAT")
same("J", "LBIRD")

# 11. Evangeline, who does not write poetry or hate rats in the air vents, is the acrobat who can
# sneak past laser security.
different("E", "LPOETRY")
different("E", "DRATS")
same("E", "SACROBAT")

# 12. Broderick eats lunch with the covert operations specialist and the spy who hates those
# annoying people who recline their seats all the way into your lap on an airplane, but does not eat
# with the spy who hates dead batteries.
same_feature("QUAD", "B", "SCOVERT", "DSEAT")
different_feature("QUAD", "B", "DBATTERY")

# 13. Demetrius eats lunch with the spy who enjoys playing solitaire on their iPhone and the spy who
# hates pockets with holes in them, but does not eat with Broderick.
same_feature("QUAD", "D", "LSOLITAIRE", "DPOCKET")
different_feature("QUAD", "D", "B")

# 14. The martial artist (who doesn’t enjoy solving crossword puzzles) eats lunch with Isabelle, but
# only one of them went to college.
different("SMARTIAL", "LXWORD")
same_feature("QUAD", "SMARTIAL", "I")
different_feature("COLLEGE", "SMARTIAL", "I")

# 15. Gwendolyn (who is not the helicopter pilot, and does not hate getting blocked by grates in
# ductwork) eats lunch with the spy who enjoys hosting silent dance parties.
different("G", "SCOPTER")
different("G", "DGRATES")
same_feature("QUAD", "G", "LPARTY")

# 16. The covert operations specialist does not enjoy whittling.
different("SCOVERT", "LWHITTLE")

# 17. Their home addresses look pretty spread out, except that Alexandria lives on the same street
# as both the spy who has awesome survival skills and the spy who enjoys factoring large numbers in
# their head (who isn’t Isabelle).
has_feature("LIVENEAR", "A", "SSURVIVE", "LFACTOR")
different("LFACTOR", "I")
problem.addConstraint(ExactSumConstraint(3), ["LIVENEAR" + SPY for SPY in SPY_NAMES])

# 18. The lock-picking expert does not hate it when Microsoft Office freezes or when pockets have
# holes in them.
different("SLOCK", "DOFFICE")
different("SLOCK", "DPOCKET")

# 19. None of the spies have served in more than one branch of the armed forces.
for SPY in SPY_NAMES:
	problem.addConstraint(SomeInSetConstraint([False]), ["ARMY" + SPY, "NAVY" + SPY])

for solution in problem.getSolutionIter():
	for spy_index, SPY in zip(spy_indexes, SPY_NAMES):
		SPY_FEATURES = [FEATURE for FEATURE in FEATURES if solution[FEATURE + SPY]]
		SPY_TRAITS = [TRAIT for TRAIT in TRAITS if solution[TRAIT] == spy_index]
		print(SPY, *SPY_FEATURES, *SPY_TRAITS)
	print()

