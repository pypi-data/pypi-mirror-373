#############################################################################
##
##  This file is read as soon as the GAP library of tables of marks is
##  available.
##  It provides the mapping between the GAP Character Table Library and the
##  GAP Library of Tables of Marks,
##  via the "tom" attribute of 'CTblLib.Data.IdEnumerator'.
##


#############################################################################
##
#V  CTblLib.Data.IdEnumerator.attributes.tom
##
Add( CTblLib.Data.attributesRelevantForGroupInfoForCharacterTable, "tom" );

DatabaseAttributeAddX( CTblLib.Data.IdEnumerator, rec(
  identifier:= "tom",
  description:= "mapping between CTblLib and GAP's library of tables of marks",
  type:= "pairs",
  datafile:= Filename( DirectoriesPackageLibrary( "ctbllib", "data" )[1],
                       "grp_tom.json" ),
  dataDefault:= [],
  isSorted:= true,
  attributeValue:= function( attr, id )
    local pos, main, name, names;

    pos:= Position( LIBLIST.TOM_TBL_INFO[2], LowercaseString( id ) );
    if pos = fail then
      main:= attr.idenumerator.attributes.IdentifierOfMainTable;
      name:= main.attributeValue( main, id );
      if name <> fail then
        pos:= Position( LIBLIST.TOM_TBL_INFO[2], LowercaseString( name ) );
      fi;
    fi;
    if pos <> fail then
      name:= LIBLIST.TOM_TBL_INFO[1][ pos ];
      names:= NamesLibTom( name );
      if names <> fail and not IsEmpty( names ) then
        name:= names[1];
      fi;
      return Concatenation( [ [ "GroupForTom", [ name ] ] ],
                 DatabaseAttributeValueDefaultX( attr, id ) );
    else
      return DatabaseAttributeValueDefaultX( attr, id );
    fi;
    end,
  eval:= function( attr, l )
    return List( l, val -> [ "GroupForTom", val ] );
    end,
  reverseEval:= function( attr, info )
    local pos, data, entry;

    if info[1] = "GroupForTom" then
      if Length( info[2] ) = 1 then
        pos:= Position( LIBLIST.TOM_TBL_INFO[1],
                        LowercaseString( info[2][1] ) );
        if pos <> fail then
          return LIBLIST.TOM_TBL_INFO[2][ pos ];
        fi;
      else
        if not IsBound( attr.data )  then
          Read( attr.datafile );
        fi;
        for data in [ attr.data.automatic, attr.data.nonautomatic ] do
          for entry in data do
            if info[2] in entry[2] then
              return entry[1];
            fi;
          od;
        od;
      fi;
    fi;
    return fail;
    end,
  neededAttributes:= [ "IsDuplicateTable", "IdentifiersOfDuplicateTables" ],
  prepareAttributeComputation:= function( attr )
    local i;

    CTblLib.Data.prepare( attr );
    CTblLib.Data.invposition:= InverseMap( LIBLIST.position );
    for i in [ 1 .. Length( CTblLib.Data.invposition ) ] do
      if IsInt( CTblLib.Data.invposition[i] ) then
        CTblLib.Data.invposition[i]:= [ CTblLib.Data.invposition[i] ];
      fi;
    od;
    CTblLib.Data.attrvalues_tom:= rec();
    end,
  cleanupAfterAttributeComputation:= function( attr )
    Unbind( CTblLib.Data.invposition );
    Unbind( CTblLib.Data.attrvalues_tom );
    CTblLib.Data.cleanup( attr );
    end,
  create:= function( attr, id )
    local main, mainid, subgroupfits, dupl, names, result, name, tbl, r,
          super, tom, mx, pos, i, orders;

    # For duplicate tables, take (and cache) the result for the main table.
    main:= attr.idenumerator.attributes.IdentifierOfMainTable;
    mainid:= main.attributeValue( main, id );
    if mainid <> fail then
      id:= mainid;
    fi;
    if IsBound( CTblLib.Data.attrvalues_tom ) and
       IsBound( CTblLib.Data.attrvalues_tom.( id ) ) then
      return CTblLib.Data.attrvalues_tom.( id );
    fi;

    # Now we know that we have to work.
    subgroupfits:= function( tom, poss, tbl )
      return First( poss,
           function( i )
             local G;
             G:= RepresentativeTom( tom, i );
             return NrConjugacyClasses( G ) = NrConjugacyClasses( tbl ) and
#T provide a utility that compares more invariants?
                    IsRecord( TransformingPermutationsCharacterTables(
                                  CharacterTable( G ), tbl ) );
           end );
    end;

    dupl:= attr.idenumerator.attributes.IdentifiersOfDuplicateTables;
    names:= Concatenation( [ id ], dupl.attributeValue( dupl, id ) );
    result:= [];

    for name in names do
      tbl:= CharacterTable( name );

      # Check for stored fusions into tables that know a table of marks.
      # (We need not store the table of marks of `tbl' itself,
      # because the `extract' function will deal with it.)
      for r in ComputedClassFusions( tbl ) do
        if Length( ClassPositionsOfKernel( r.map ) ) = 1 then
          super:= CharacterTable( r.name );
          if super <> fail and HasFusionToTom( super ) then
            # Identify the subgroup.
            tom:= TableOfMarks( super );
            if IsBound( r.specification ) and 4 < Length( r.specification )
               and r.specification{ [ 1 .. 4 ] } = "tom:" then
              # Restrict the test to the given subgroup.
              pos:= r.specification;
              pos:= Int( pos{ [ 5 .. Length( pos ) ] } );
              if IsInt( pos ) then
                i:= subgroupfits( tom, [ pos ], tbl );
                if i <> fail then
                  Add( result, [ Identifier( tom ), i ] );
#T and else? print an error because of the wrong stored value?
                fi;
              else
                Info( InfoDatabaseAttributeX, 1,
                      "specification ", r.specification,
                      " in table ", name, "?" );
              fi;
            elif HasMaxes( super ) and id in Maxes( super ) then
              mx:= MaximalSubgroupsTom( tom );
              if Sum( SizesConjugacyClasses( super ){ Set( r.map ) } )
                   = Size( tbl ) then
                pos:= Filtered( [ 1 .. Length( mx[2] ) ],
                                i -> mx[2][i] = 1 );
              else
                pos:= Filtered( [ 1 .. Length( mx[2] ) ],
                          i -> mx[2][i] = Size( super ) / Size( tbl ) );
              fi;
              if Length( pos ) = 1 then
                # Omit the check.
                Add( result, [ Identifier( tom ), mx[1][ pos[1] ] ] );
              else
                i:= subgroupfits( tom, mx[1]{ pos }, tbl );
                if i <> fail then
                  Add( result, [ Identifier( tom ), i ] );
                fi;
              fi;
            else
              # Loop over all classes of subgroups of the right order.
              orders:= OrdersTom( tom );
              pos:= Filtered( [ 1 .. Length( orders ) ],
                        i -> orders[i] = Size( tbl ) );
              i:= subgroupfits( tom, pos, tbl );
              if i <> fail then
                Add( result, [ Identifier( tom ), i ] );
              fi;
            fi;
          fi;
        fi;
      od;
    od;

    if IsEmpty( result ) then
      result:= attr.dataDefault;
    else
      result:= Set( result );
    fi;

    # Cache the result.
    CTblLib.Data.attrvalues_tom.( id ):= result;

    return result;
    end,
  string:= entry -> CTblLib.AttrDataString( entry, [], false ),
  check:= ReturnTrue,
  ) );

# # Create the analogous attribute of 'CTblLib.Data.IdEnumeratorExt',
# # and set also the 'eval' component.
# CTblLib.ExtendAttributeOfIdEnumeratorExt( "tom", true );
# 
# # Set the attribute values that may have been added up to now.
# # (As soon as the SpinSym package gets loaded, it notifies some data.)
# CTblLib.Data.IdEnumeratorExt.attributes.tom.data.automatic:=
#     CTblLib.IdEnumeratorExt_attributes_tom_data_automatic;

