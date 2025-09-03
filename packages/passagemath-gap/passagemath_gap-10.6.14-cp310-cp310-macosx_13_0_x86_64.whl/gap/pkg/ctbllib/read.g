#############################################################################
##
#W  read.g               GAP 4 package CTblLib                  Thomas Breuer
##

# Notify functions concerning Deligne-Lusztig names.
DeclareAutoreadableVariables( "ctbllib", "dlnames/dllib.g",
    [ "DeltigLibUnipotentCharacters", "DeltigLibGetRecord" ] );

# Read the implementation part.
ReadPackage( "ctbllib", "gap4/ctadmin.gi" );
if IsPackageMarkedForLoading( "TomLib", ">= 1.0" )
   and not IsBound( GAPInfo.PackageExtensionsLoaded ) then
  ReadPackage( "ctbllib", "gap4/tomlib_only.g" );
fi;
ReadPackage( "ctbllib", "gap4/construc.gi" );
ReadPackage( "ctbllib", "gap4/ctblothe.gi" );
ReadPackage( "ctbllib", "gap4/test.g" );

# Read functions concerning Deligne-Lusztig names.
ReadPackage( "ctbllib", "dlnames/dlnames.gi" );
if IsPackageMarkedForLoading( "chevie", ">= 1.0" )
   and not IsBound( GAPInfo.PackageExtensionsLoaded ) then
  DeclareAutoreadableVariables( "ctbllib", "dlnames/dlconstr.g",
      [ "DeltigConstructionFcts" ] );
  DeclareAutoreadableVariables( "ctbllib", "dlnames/dltest.g",
      [ "DeltigTestFcts", "DeltigTestFunction" ] );
fi;

# Initialize database attributes
# and Browse overviews of tables, irrationalities, and differences of data.
# (The data will be modified as soon as the Browse package will become
# available.)
ReadPackage( "ctbllib", "gap4/ctbltoct.g" );
CTblLib.Data.IdEnumerator:= rec( attributes:= rec(), identifiers:= [] );
CTblLib.Data.IdEnumeratorExt:= rec( attributes:= rec(), identifiers:= [] );
CTblLib.Data.attributesRelevantForGroupInfoForCharacterTable:= [];
CTblLib.IdEnumeratorExt_attributes_atlas_data_automatic:= [];
CTblLib.SpinSymNames:= [];

# Use the code in CTblLib to build an id enumerator, independent of Browse.
ReadPackage( "ctbllib", "gap4/ctdbattr.g" );

# Load ATLAS related stuff.
ReadPackage( "ctbllib", "gap4/od.g" );
ReadPackage( "ctbllib", "gap4/atlasstr.g" );
ReadPackage( "ctbllib", "gap4/atlasirr.g" );

# Load stuff depending on Browse if applicable.
if IsPackageMarkedForLoading( "Browse", "1.8.10" )
   and not IsBound( GAPInfo.PackageExtensionsLoaded ) then
  if IsPackageMarkedForLoading( "AtlasRep", "2.1" ) then
    ReadPackage( "ctbllib", "gap4/atlasrep_only.g" );
  fi;
  ReadPackage( "ctbllib", "gap4/browse_only.g" );
fi;


#############################################################################
##
#E

