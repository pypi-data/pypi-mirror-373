# This file is needed only for technical reasons.
# We cannot execute the calls already when SpinSym notifies the tables,
# because the package extension that belongs to the Browse package
# is not yet loaded in this situation.
Perform( CTblLib.SpinSymNames, CTblLib.SetAttributesForSpinSymTable );
