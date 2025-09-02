# S -> NP VP
from greenideas.attributes.aspect import Aspect
from greenideas.attributes.attribute_type import AttributeType
from greenideas.attributes.case import Case
from greenideas.attributes.npform import NPForm
from greenideas.attributes.person import Person
from greenideas.attributes.voice import Voice
from greenideas.parts_of_speech.pos_types import POSType
from greenideas.rules.expansion_spec import INHERIT, ExpansionSpec
from greenideas.rules.grammar_rule import GrammarRule
from greenideas.rules.source_spec import SourceSpec

s__np_vp = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.ANIMACY: INHERIT,
                AttributeType.CASE: Case.NOMINATIVE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
            },
        ),
        ExpansionSpec(
            POSType.VP,
            {
                AttributeType.ANIMACY: INHERIT,
                AttributeType.ASPECT: Aspect.SIMPLE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.VOICE: INHERIT,
            },
        ),
    ],
)

# S -> NP AuxP
s__np_auxp = GrammarRule(
    SourceSpec(
        POSType.S,
        {
            AttributeType.VOICE: Voice.ACTIVE,
        },
    ),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.ANIMACY: INHERIT,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.CASE: Case.NOMINATIVE,
            },
        ),
        ExpansionSpec(
            POSType.AuxP,
            {
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.TENSE: INHERIT,
            },
        ),
    ],
)

# S -> NP ModalP
s__np_modalp = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.ANIMACY: INHERIT,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.CASE: Case.NOMINATIVE,
            },
        ),
        ExpansionSpec(
            POSType.ModalP,
            {
                AttributeType.TENSE: INHERIT,
            },
        ),
    ],
)

# S -> S Conj S
s__s_conj_s = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(POSType.S),
        ExpansionSpec(POSType.CoordConj),
        ExpansionSpec(POSType.S),
    ],
    weight=0.2,
    ignore_after_depth=2,
)

s__s_sub_s = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(POSType.S),
        ExpansionSpec(POSType.Subordinator),
        ExpansionSpec(POSType.S),
    ],
    weight=0.2,
    ignore_after_depth=2,
)

s__np_be_adjp = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.CASE: Case.NOMINATIVE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
            },
        ),
        ExpansionSpec(
            POSType.Be,
            {
                AttributeType.ASPECT: Aspect.SIMPLE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.TENSE: INHERIT,
            },
        ),
        ExpansionSpec(POSType.AdjP),
    ],
)

s__np_be_np = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.CASE: Case.NOMINATIVE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
            },
        ),
        ExpansionSpec(
            POSType.Be,
            {
                AttributeType.ASPECT: Aspect.SIMPLE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.TENSE: INHERIT,
            },
        ),
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.CASE: Case.NOMINATIVE,
                AttributeType.NPFORM: NPForm.LEXICAL,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: Person.THIRD,
            },
        ),
    ],
    weight=0.3,
)

s__np_be_pp = GrammarRule(
    SourceSpec(POSType.S),
    [
        ExpansionSpec(
            POSType.NP,
            {
                AttributeType.CASE: Case.NOMINATIVE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
            },
        ),
        ExpansionSpec(
            POSType.Be,
            {
                AttributeType.ASPECT: Aspect.SIMPLE,
                AttributeType.NUMBER: INHERIT,
                AttributeType.PERSON: INHERIT,
                AttributeType.TENSE: INHERIT,
            },
        ),
        ExpansionSpec(POSType.PP),
    ],
)

s_expansions = [
    s__np_vp,
    s__np_auxp,
    s__np_modalp,
    s__s_conj_s,
    s__s_sub_s,
    s__np_be_adjp,
    s__np_be_np,
    s__np_be_pp,
]
