#############################################################################
##
##  This file is read as soon as the GAP library of tables of marks
##  is available.
##  Afterwards the information about identifiers of the tables is stored in
##  'LIBLIST.TOM_TBL_INFO',
##  and methods for 'FusionCharTableTom' and 'CharacterTable' (for a table of
##  marks from the library) are installed.
##

CallFuncList( function()
  local dir, file, str, evl;

  dir:= DirectoriesPackageLibrary( "ctbllib", "data" );
  file:= Filename( dir[1], "tom_tbl.json" );
  str:= StringFile( file );
  if str = fail then
    Error( "the data file '", file, "' is not available" );
  fi;
  evl:= MakeImmutable( EvalString( str ) );
  LIBLIST.TOM_TBL_INFO_VERSION:= evl[1];
  LIBLIST.TOM_TBL_INFO:= evl{ [ 2, 3 ] };
  end, [] );


#############################################################################
##
#M  FusionCharTableTom( <tbl>, <tom> )  . . . . . . . . . . .  element fusion
##
##  <#GAPDoc Label="FusionCharTableTom">
##  <ManSection>
##  <Meth Name="FusionCharTableTom" Arg="tbl, tom"/>
##
##  <Description>
##  Let <A>tbl</A> be an ordinary character table from the
##  &GAP; Character Table Library
##  with the attribute <Ref Attr="FusionToTom"/>,
##  and let <A>tom</A> be the table of marks from the &GAP; package
##  <Package>TomLib</Package> that corresponds to <A>tbl</A>.
##  In this case,
##  a method for <Ref Oper="FusionCharTableTom" BookName="ref"/>
##  is available that returns the fusion from <A>tbl</A> to <A>tom</A> that
##  is given by the <Ref Attr="FusionToTom"/> value of <A>tbl</A>.
##  <P/>
##  <Example>
##  gap> tbl:= CharacterTable( "A5" );
##  CharacterTable( "A5" )
##  gap> tom:= TableOfMarks( "A5" );
##  TableOfMarks( "A5" )
##  gap> FusionCharTableTom( tbl, tom );
##  [ 1, 2, 3, 5, 5 ]
##  </Example>
##  </Description>
##  </ManSection>
##  <#/GAPDoc>
##
InstallMethod( FusionCharTableTom,
    [ "IsOrdinaryTable and IsLibraryCharacterTableRep and HasFusionToTom",
      "IsTableOfMarks and IsLibTomRep" ],
    function( tbl, tom )
    local fus;

    fus:= FusionToTom( tbl );
    if fus.name <> Identifier( tom ) then
      TryNextMethod();
    fi;
    fus:= fus.map;
    if HasPermutationTom( tom ) then
      fus:= OnTuples( fus, PermutationTom( tom ) );
    fi;
    if HasClassPermutation( tbl ) then
      fus:= Permuted( fus, ClassPermutation( tbl ) );
    fi;

    return fus;
    end );


#############################################################################
##
#M  CharacterTable( <tom> ) . . . . . . . . . . . . . .  for a table of marks
##
##  If <tom> is a library table of marks then we check whether there is a
##  corresponding character table in the library.
##  If there is no such character table but <tom> stores an underlying group
##  then we delegate to this group.
##  Otherwise we return `fail'.
##
##  <#GAPDoc Label="CharacterTable_for_tom">
##  <ManSection>
##  <Meth Name="CharacterTable" Arg="tom" Label="for a table of marks"/>
##
##  <Description>
##  For a table of marks <A>tom</A>, this method for
##  <Ref Oper="CharacterTable" Label="for a group" BookName="ref"/>
##  returns the character table corresponding to <A>tom</A>.
##  <P/>
##  If <A>tom</A> comes from the <Package>TomLib</Package>
##  package, the character table comes from the
##  &GAP; Character Table Library.
##  Otherwise, if <A>tom</A> stores an
##  <Ref Func="UnderlyingGroup" BookName="ref"/> value then
##  the task is delegated to a
##  <Ref Oper="CharacterTable" Label="for a group" BookName="ref"/> method
##  for this group,
##  and if no underlying group is available then <K>fail</K> is returned.
##  <P/>
##  <Example>
##  gap> CharacterTable( TableOfMarks( "A5" ) );
##  CharacterTable( "A5" )
##  </Example>
##  </Description>
##  </ManSection>
##  <#/GAPDoc>
##
InstallOtherMethod( CharacterTable,
    [ "IsTableOfMarks" ],
    function( tom )
    local pos;

    if IsLibTomRep( tom ) then
      pos:= Position( LIBLIST.TOM_TBL_INFO[1],
                      LowercaseString( Identifier( tom ) ) );
      if pos <> fail then
        return CharacterTable( LIBLIST.TOM_TBL_INFO[2][ pos ] );
      fi;
    elif HasUnderlyingGroup( tom ) then
      return CharacterTable( UnderlyingGroup( tom ) );
    fi;
    return fail;
    end );


#############################################################################
##
#E

