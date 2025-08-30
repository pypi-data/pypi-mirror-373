from indigo import Indigo, IndigoObject
from indigo.inchi import IndigoInchi
from indigo.renderer import IndigoRenderer

indigo = Indigo()
renderer = IndigoRenderer(indigo)
indigo.setOption("render-output-format", "svg")
indigo.setOption("ignore-stereochemistry-errors", True)
indigo.setOption("render-stereo-style", "ext")
indigo.setOption("aromaticity-model", "generic")
indigo.setOption("render-coloring", True)
indigo.setOption("molfile-saving-mode", "3000")
indigo.setOption("dearomatize-verification", False)
indigo_inchi = IndigoInchi(indigo)


def get_aromatic_dearomatic_forms(m: IndigoObject):
    """
    Get the aromatic and dearomatic forms of the molecule. Retain the original form if it's not inversible.
    Inversible: after aromatic-dearomatic-aromatic transformation, the molecule is the same as the first aromatic transformation.
    :param m: molecule from indigo.
    :return: pair of indigo objects, first is aromatic, second is dearomatic.
    """
    try:
        aromatic_reaction = m.clone()
        aromatic_reaction.aromatize()
        dearomatic_reaction = aromatic_reaction.clone()
        dearomatic_reaction.dearomatize()
        second_aromatic_reaction = dearomatic_reaction.clone()
        second_aromatic_reaction.aromatize()
        match = indigo.exactMatch(aromatic_reaction, second_aromatic_reaction)
        if match:
            return aromatic_reaction, dearomatic_reaction
        else:
            return m, dearomatic_reaction
    except (Exception):
        # If aromatization then following deromatization fails, we just skip it.
        dearomatic_reaction = m.clone()
        dearomatic_reaction.dearomatize()
        return m, dearomatic_reaction


# Function to process dative bonds in a molecule
# Returns True if at least one dative bond (_BOND_COORDINATION) was removed
def remove_dative_bonds_in_mol(molecule: IndigoObject) -> bool:
    """
    Remove all dative bonds in a molecule or a query molecule.
    :param molecule: The molecule to remove.
    :return: Whether there are any dative bonds in the molecule that were removed.
    """
    dative_bond_removed = False  # Flag to track if any dative bond was removed

    bonds_idx_to_remove = []
    for bond in molecule.iterateBonds():
        # Check if the bond is of a dative type (_BOND_COORDINATION = 9)
        if bond.bondOrder() == 9:  # _BOND_COORDINATION
            atom1 = bond.source()
            atom2 = bond.destination()

            # Print bond details for debugging
            print(f"Processing dative bond between atoms {atom1.index()} and {atom2.index()}")

            # Cache bond information
            # bond.setBondOrder(1)
            bonds_idx_to_remove.append(bond.index())
            dative_bond_removed = True  # Set flag to True

    if not dative_bond_removed:
        return False

    molecule.removeBonds(bonds_idx_to_remove)
    return True  # Return whether any dative bond was removed


def remove_dative_in_reaction(reaction: IndigoObject) -> bool:
    """
    Remove all dative bonds in a reaction or a query reaction, from all reactants and products.
    :param reaction: The reaction to remove dative bonds.
    :return: Whether there are any dative bonds in the reaction that were removed.
    """
    reactant_dative_removed: bool = any(
        remove_dative_bonds_in_mol(reactant) for reactant in reaction.iterateReactants())
    product_dative_removed: bool = any(remove_dative_bonds_in_mol(product) for product in reaction.iterateProducts())
    return reactant_dative_removed or product_dative_removed


def highlight_mol_substructure(query: IndigoObject, sub_match: IndigoObject):
    """
    Highlight the bonds and atoms for substructure search result.

    :param sub_match: The substructure search match obtained from indigo.substructureMatcher(mol).match(query).
    :param query: The query we were running to match the original structure.
    """
    for qatom in query.iterateAtoms():
        atom = sub_match.mapAtom(qatom)
        if atom is None:
            continue
        atom.highlight()

        for nei in atom.iterateNeighbors():
            if not nei.isPseudoatom() and not nei.isRSite() and nei.atomicNumber() == 1:
                nei.highlight()
                nei.bond().highlight()

    for bond in query.iterateBonds():
        bond = sub_match.mapBond(bond)
        if bond is None:
            continue
        bond.highlight()


def highlight_reactions(query_reaction_smarts: IndigoObject, reaction_match: IndigoObject):
    """
    Highlight the bonds and atoms for substructure search result of reaction that's in the query and survived the mapping.

    :param query_reaction_smarts: The query we ran substructure search on.
    :param reaction_match: The substructure search match obtained from indigo.substructureMatcher(reaction).match(query).
    :return:
    """
    for q_mol in query_reaction_smarts.iterateMolecules():
        matched_mol = reaction_match.mapMolecule(q_mol)
        sub_match = indigo.substructureMatcher(matched_mol).match(q_mol)
        highlight_mol_substructure(q_mol, sub_match)
