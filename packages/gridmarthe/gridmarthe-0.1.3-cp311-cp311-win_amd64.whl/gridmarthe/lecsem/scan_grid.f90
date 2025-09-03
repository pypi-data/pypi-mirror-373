! SPDX-License-Identifier: GPL-3.0-or-later
! Copyright 2024, BRGM
! 
! This file is part of gridmarthe.
! 
! Gridmarthe is free software: you can redistribute it and/or modify it under the
! terms of the GNU General Public License as published by the Free Software
! Foundation, either version 3 of the License, or (at your option) any later
! version.
! 
! Gridmarthe is distributed in the hope that it will be useful, but WITHOUT ANY
! WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
! PARTICULAR PURPOSE. See the GNU General Public License for more details.
! 
! You should have received a copy of the GNU General Public License along with
! Gridmarthe. If not, see <https://www.gnu.org/licenses/>.
!
MODULE MODGRIDMARTHE
!   MODGRIDMARTHE
!   -------------
!   Module using lecsem/edsemi subroutines for python wrapper
!   coding: utf-8
!
!   Author/Developper:
!       JP Vergnes, 2021
!       A. Manlay,  2022-2023
!
    INTEGER :: LEC                      ! Unité de lecture
    INTEGER :: IOUCON                   ! Ecriture sur la console (<0 non, 0 = erreurs, >0 = tout)
    INTEGER :: NLIG, NKOL               ! Nombre maximum de ligne et de colonne / en retour nbre de ligne et de colonne
    INTEGER :: NTOT                     ! Nombre maxi de places dans le tableau FONC()
                                        ! NTOT  = Nombre de points = NKOL * NLIG
                                        ! N.B. : Si NTOT = 0 => On ne lit pas les points
                                        !        mais seulement les coordonnées (Il n'y a rien dans FONC)
    INTEGER :: INVERS                   ! INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
                                        !      : 1 = Inversion la première ligne lue est rangée en dernier
                                        !            et YLIG est inversé aussi (logiciels d'interpolation)
    INTEGER :: LIRE_DXDY                ! LIRE_DXDY : 0 = On ne veut pas lire de DX() et DY()
                                        !                (On les saute s'ils existent)
                                        !           : 1 = On veut lire les DX() et DY() (s'ils existent)
    CHARACTER (LEN=132)  :: TITSEM      ! TITSEM = Dernier titre lu pour la Grille (len=132)
    INTEGER :: LU_DXDY                  ! LU_DXDY : 0 = On n'a pas lu de DX et DY
                                        !         : 1 = On a lu des DX et DY
    INTEGER :: LU_XY                    ! LU_XY   : 0 = On n'a pas lu de X() et Y() : Par ex lecture en format libre
                                        !         : 1 = On a lu des X() et Y()
    REAL, DIMENSION(999) :: XCOL        ! XCOL  = Tableau des abscisses (si LU_XY > 0)
    REAL, DIMENSION(999) :: YLIG        ! YLIG  = Tableau des ordonnées (si LU_XY > 0)
    REAL, DIMENSION(999) :: DXLU        ! DXLU  = DX lus si LU_DXDY > 0
    REAL, DIMENSION(999) :: DYLU        ! DYLU  = DY lus si LU_DXDY > 0
    REAL  :: X0                         ! X0    = Abscisse du cote ouest de la colonne n°1    (si LU_XY > 0)
    REAL  :: Y0                         ! Y0    = Ordonnée du    bas     de la ligne   n°NLIG (si LU_XY > 0)
    REAL  :: DATE                       ! DATE     = Date associée à la Grille
    REAL, DIMENSION(999*999) :: FONC    ! FONC  = Tableau des valeurs lues
    INTEGER :: IERLEC                   ! IERLEC =  0 Si normal
                                        ! IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
                                        ! IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
                                        ! IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
                                        ! IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
    INTEGER    :: IANALY                ! IANALY : 0 = Lecture normale
                                        !        : 1 = Prélecture rapide (pour analyser les dimensions etc)
                                        !              FONC(), XCOL(), YLIG() ne sont pas valorisés
                                        !              (N.B. Si binaire => Pas plus rapide)
    CHARACTER (LEN=132) :: TYP_DON      ! TYP_DON  = Type de donnée (len=13)
    CHARACTER (LEN=7)   :: TYP_DON3     ! TYP_DON3 = Complément du type de donnée (len=7)
    CHARACTER (LEN=132) :: LIBCHIM      ! LIBCHIM  = Libellé complémentaire (nom de l'Élément Chimique) (len=80)
    INTEGER    :: N_ELEMCH              ! N_ELEMCH = Numéro associé au type de donnée (élément Chimique)
    INTEGER    :: ISTEP                 ! ISTEP    = Numéro du pas de temps (-9999 si pas lu)
    INTEGER    :: N_COUCH               ! N_COUCH  = Numéro de la Couche
    INTEGER    :: NU_ZOO                ! NU_ZOO   = Numéro du Gigogne (0 = Main)
    INTEGER    :: NUMERR                ! Maille NUMERR
    INTEGER    :: NCOUC_MX              ! NCOUC_MX = Nombre maxi de Couches
    INTEGER    :: NU_ZOOMX              ! NU_ZOOMX = Nombre maxi de Gigognes

CONTAINS

    SUBROUTINE SCAN_NU_ZOOMX(XFILE, KNU_ZOOMX)
        !
        IMPLICIT NONE
        !
        CHARACTER (LEN=132), INTENT(IN) :: XFILE
        INTEGER, INTENT(OUT) :: KNU_ZOOMX
        !
        INTEGER :: INUMSTEP
        !
        LIRE_DXDY =  0
        IANALY    =  1
        INVERS    =  0
        IOUCON    = -1
        LEC       = 10
        IERLEC    =  0
        N_COUCH   =  0
        NU_ZOO    =  0
        INUMSTEP  =  0
        !
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
        !
        CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
                  , IOUCON, LEC, IERLEC, NUMERR, NTOT &
                  , IANALY &
                  , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                  , DATE, LIBCHIM &
                  , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
        !
        KNU_ZOOMX = NU_ZOOMX
        !
        CLOSE(10)
        !
    END SUBROUTINE SCAN_NU_ZOOMX
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! =============================================================================!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    SUBROUTINE SCAN_DIM(XFILE, XTYP_DON, KNU_ZOOMX, KDIMEN, KNBSTEP)
        !
        IMPLICIT NONE
        !
        CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
        INTEGER, INTENT(IN)                           :: KNU_ZOOMX
        INTEGER, DIMENSION(KNU_ZOOMX + 1, 3), INTENT(OUT) :: KDIMEN
        INTEGER, INTENT(OUT)                          :: KNBSTEP
        !
        INTEGER :: ISTEP_TEMP
        !
        LIRE_DXDY =  0
        IANALY    =  1
        INVERS    =  0
        IOUCON    = -1
        LEC       = 10
        IERLEC    =  0
        N_COUCH   =  0
        NU_ZOO    =  0
        KNBSTEP   =  0
        !
        ISTEP_TEMP = -1
        !
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
        !
        DO WHILE (IERLEC == 0)
            CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
                      , IOUCON, LEC, IERLEC, NUMERR, NTOT &
                      , IANALY &
                      , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                      , DATE, LIBCHIM &
                      , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
            IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
                KDIMEN(NU_ZOO + 1, 1) = NKOL
                KDIMEN(NU_ZOO + 1, 2) = NLIG
                KDIMEN(NU_ZOO + 1, 3) = NCOUC_MX
                IF (ISTEP /= ISTEP_TEMP) THEN
                    KNBSTEP = KNBSTEP + 1
                    ISTEP_TEMP = ISTEP
                ENDIF
            ENDIF
        ENDDO
        !
        CLOSE(LEC)
        !
    END SUBROUTINE SCAN_DIM
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! =============================================================================!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    SUBROUTINE READ_GRID(XFILE, XTYP_DON, KNBSTEP, KNBTOT, KNU_ZOOMX, PVAR, PDATES, &
        KSTEPS, PXCOL, PYLIG, PDXLU, PDYLU, TITSEM)
        !
        IMPLICIT NONE
        !
        CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
        INTEGER, INTENT(IN)                           :: KNBTOT
        INTEGER, INTENT(IN)                           :: KNBSTEP
        INTEGER, INTENT(IN)                           :: KNU_ZOOMX
        INTEGER, DIMENSION(KNBSTEP), INTENT(OUT)      :: KSTEPS
        REAL(KIND=4), DIMENSION(KNBSTEP), INTENT(OUT) :: PDATES
        REAL(KIND=4), DIMENSION(KNU_ZOOMX + 1, 999), INTENT(OUT) :: PXCOL, PYLIG, PDXLU, PDYLU
        REAL(KIND=8), DIMENSION(KNBSTEP, KNBTOT), INTENT(OUT) :: PVAR
        CHARACTER (LEN=132), INTENT(OUT)              :: TITSEM             ! Modifs AM: ajout TITSEM dans les sorties de la subroutine (+ ajout en `dummy argument` càd réf dans la list d'arg de la procedure)
        !
        INTEGER    :: ISTEPINC, ISTEP_TEMP, INTOT_TEMP
        ! LOGICAL    :: debug
        !
        LIRE_DXDY =  1
        IANALY    =  0
        INVERS    =  0
        IOUCON    = -1
        LEC       = 10
        IERLEC    =  0
        !
        N_COUCH = 0
        NU_ZOO  = 0
        ISTEP   = 0
        !
        PVAR (:, :) = 1e+20
        PXCOL(:, :) = 1e+20
        PYLIG(:, :) = 1e+20
        PDXLU(:, :) = 1e+20
        PDYLU(:, :) = 1e+20
        !
        ISTEPINC   =  0
        ISTEP_TEMP = -1
        INTOT_TEMP =  1
        !
        ! debug = .FALSE.               
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
        !
        DO WHILE (IERLEC == 0)
            NLIG = 999.
            NKOL = 999.
            NTOT = NLIG * NKOL
            NCOUC_MX = 99.
            NU_ZOOMX = 99.
            CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
                      , IOUCON, LEC, IERLEC, NUMERR, NTOT &
                      , IANALY &
                      , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                      , DATE, LIBCHIM &
                      , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
            IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
                IF (ISTEP /= ISTEP_TEMP) THEN
                    ISTEPINC = ISTEPINC + 1
                    ISTEP_TEMP = ISTEP
                    INTOT_TEMP = 1
                    KSTEPS(ISTEPINC) = ISTEP
                    PDATES(ISTEPINC) = real(DATE, 4)
                ENDIF
                IF (ISTEPINC == 1 .AND. N_COUCH == 1) THEN
                    PXCOL(NU_ZOO + 1, :NKOL) = real(XCOL(:NKOL), 4)
                    PYLIG(NU_ZOO + 1, :NLIG) = real(YLIG(:NLIG), 4)
                    PDXLU(NU_ZOO + 1, :NKOL) = real(DXLU(:NKOL), 4)
                    PDYLU(NU_ZOO + 1, :NLIG) = real(DYLU(:NLIG), 4)
                ENDIF
                PVAR(ISTEPINC, INTOT_TEMP:INTOT_TEMP + NTOT -1) = FONC(:NTOT)
                INTOT_TEMP = INTOT_TEMP + NTOT
            ! if(debug) print *, 'ERRLEC:', IERLEC, 'At step:', ISTEPINC, 'in layer:', N_COUCH, 'at mesh:', NUMERR
            ENDIF
        ENDDO
        !
        CLOSE(LEC)
        !
    END SUBROUTINE READ_GRID
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! =============================================================================!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    SUBROUTINE READ_GRID_SHALLOW(XFILE, XTYP_DON, KNBSTEP, KN_COUCHMX, KNBTOT, &
        KNU_ZOOMX, PVAR, PDATES, KSTEPS, PXCOL, PYLIG, PDXLU, PDYLU, TITSEM)
        !
        IMPLICIT NONE
        !
        CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
        INTEGER, INTENT(IN)                           :: KNBTOT
        INTEGER, INTENT(IN)                           :: KNBSTEP
        INTEGER, INTENT(IN)                           :: KN_COUCHMX
        INTEGER, INTENT(IN)                           :: KNU_ZOOMX
        INTEGER, DIMENSION(KNBSTEP), INTENT(OUT)      :: KSTEPS
        REAL(KIND=4), DIMENSION(KNBSTEP), INTENT(OUT) :: PDATES
        REAL(KIND=4), DIMENSION(KNU_ZOOMX + 1, 999), INTENT(OUT) :: PXCOL, PYLIG, PDXLU, PDYLU
        REAL(KIND=8), DIMENSION(KNBSTEP, KNU_ZOOMX + 1, KNBTOT), INTENT(OUT) :: PVAR
        CHARACTER (LEN=132), INTENT(OUT)              :: TITSEM
        !
        !
        INTEGER    :: ISTEPINC, ISTEP_TEMP, INTOT_TEMP, N_COUCH2
        INTEGER, DIMENSION(KNU_ZOOMX + 1, 3) :: KDIMEN
        REAL(KIND=8), DIMENSION(KNBSTEP, KNU_ZOOMX + 1, KN_COUCHMX, KNBTOT) :: ZTEMP
        !
        !
        LIRE_DXDY =  1
        IANALY    =  0
        INVERS    =  0
        IOUCON    = -1
        LEC       = 10
        IERLEC    =  0
        !
        N_COUCH = 0
        NU_ZOO  = 0
        ISTEP   = 0
        !
        ZTEMP(:,:,:,:) = 9999.
        PXCOL(:, :) = 1e+20
        PYLIG(:, :) = 1e+20
        PDXLU(:, :) = 1e+20
        PDYLU(:, :) = 1e+20
        !
        ISTEPINC   =  0
        ISTEP_TEMP = -1
        INTOT_TEMP =  1
        !
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
        !
        DO WHILE (IERLEC == 0)
            NLIG = 999.
            NKOL = 999.
            NTOT = NLIG * NKOL
            NCOUC_MX = 99.
            NU_ZOOMX = 99.
            CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
                      , IOUCON, LEC, IERLEC, NUMERR, NTOT &
                      , IANALY &
                      , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                      , DATE, LIBCHIM &
                      , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
            IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
                KDIMEN(NU_ZOO + 1, 1) = NKOL
                KDIMEN(NU_ZOO + 1, 2) = NLIG
                KDIMEN(NU_ZOO + 1, 3) = NCOUC_MX
                IF (ISTEP /= ISTEP_TEMP) THEN
                    ISTEPINC = ISTEPINC + 1
                    ISTEP_TEMP = ISTEP
                    INTOT_TEMP = 1
                    KSTEPS(ISTEPINC) = ISTEP
                    PDATES(ISTEPINC) = real(DATE, 4)
                ENDIF
                IF (ISTEPINC == 1 .AND. N_COUCH == 1) THEN
                    PXCOL(NU_ZOO + 1, :NKOL) = real(XCOL(:NKOL), 4)
                    PYLIG(NU_ZOO + 1, :NLIG) = real(YLIG(:NLIG), 4)
                    PDXLU(NU_ZOO + 1, :NKOL) = real(DXLU(:NKOL), 4)
                    PDYLU(NU_ZOO + 1, :NLIG) = real(DYLU(:NLIG), 4)
                ENDIF
                ZTEMP(ISTEPINC, NU_ZOO + 1, N_COUCH, :NTOT) = FONC(:NTOT)
            ENDIF
        ENDDO
        !
        CLOSE(LEC)
        !
        PVAR(:,:,:) = 9999.
        DO NU_ZOO = 1, NU_ZOOMX + 1
            NTOT = KDIMEN(NU_ZOO, 1)*KDIMEN(NU_ZOO, 2)
            DO N_COUCH = 1, KN_COUCHMX
                WHERE (ZTEMP(:, NU_ZOO, N_COUCH, :NTOT) /= 9999.)
                    PVAR(:, NU_ZOO, :NTOT) = ZTEMP(:, NU_ZOO, N_COUCH, :NTOT)
                END WHERE
                DO N_COUCH2 = N_COUCH, KN_COUCHMX
                    WHERE (PVAR(:, NU_ZOO, :NTOT) /= 9999.) ZTEMP(:, NU_ZOO, N_COUCH2, :NTOT) = 9999.
                ENDDO
            ENDDO
        ENDDO
        !
        WHERE(PVAR(:,:,:) == 9999.) PVAR(:,:,:) = 1e+20
        !
    END SUBROUTINE READ_GRID_SHALLOW
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! =============================================================================!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    SUBROUTINE SCAN_TYPEVAR(XFILE, ZTYP_DON)
        !
        ! Get list of available var in gridfile
        ! 
        IMPLICIT NONE
        !
        CHARACTER (LEN=132), INTENT(IN)                 :: XFILE
        CHARACTER (LEN=13) , DIMENSION(99), INTENT(OUT) :: ZTYP_DON
        !
        INTEGER :: IT
        INTEGER :: N_DIM = 99
        !
        ! module defined
        LIRE_DXDY =  0
        IANALY    =  1 ! lecture rapide: var, x, y non valorisés
        INVERS    =  0 ! on n'inverse pas la lecture; la première val lue est rangée en première
        IOUCON    = -1 ! Ecriture sur la console (<0 non, 0 = erreurs, >0 = tout)
        LEC       = 10 ! unité de lecture
        IERLEC    =  0 ! erreur, on initie à 0 => all good.
        ! TODO N_ELEMCH ?
        !
        IT = 1
        !
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
        !
        DO WHILE (IERLEC == 0)
            CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
                      , IOUCON, LEC, IERLEC, NUMERR, NTOT &
                      , IANALY &
                      , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                      , DATE, LIBCHIM &
                      , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
                      
            IF (IERLEC == 0 .AND. .not.(is_in_array_strings(TYP_DON, ZTYP_DON, N_DIM)) ) THEN
                ZTYP_DON(IT) = TYP_DON
                IT = IT + 1
            ENDIF
        !
        ENDDO
        !
        CLOSE(LEC)
        !
    END SUBROUTINE SCAN_TYPEVAR
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !
    function is_in_array_strings(element, array, n_dim) result(test)
        implicit none
        integer :: it, n_dim
        logical :: test
        character(len=13) :: element
        character(len=13), dimension(n_dim) :: array
        
        test = .FALSE.
        do it = 1, n_dim
            if ( element == array(it) ) then
                test = .TRUE.
                exit ! quit do loop on first true
            endif
        enddo
        
    end function is_in_array_strings
    !
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !
    SUBROUTINE WRITE_GRID(ZVAR, XCOL, YLIG, DXLU, DYLU, TYP_DON, TITSEM, &
                          N_DIMS, NVAL, NGRID, NSTEPS, DATES, XFILE, DEBUG, IEREDI)
        ! --- Write array to Marthe Grid format (v9.0) ---
        ! ZVAR should not have missing value (if nan, set 9999. before writing !)
        ! BUT, ZVAR should contain all possible value (9999. if nan but do NOT drop nan before)
        ! ZVAR shoult be sorted according to sorted indexes (in this order) : 
        !       Time(asc), GRID(main/gig, asc) LAYER(asc), YCOL (dsc), XCOL (asc)
        IMPLICIT NONE
        !
        !inputs
        integer, intent(in)                          :: NVAL, NGRID, NSTEPS
        integer, intent(in), dimension(NGRID, 3)     :: N_DIMS
        real(kind=8), intent(in), dimension(NSTEPS, NVAL) :: ZVAR
        real(kind=4), intent(in), dimension(NVAL)         :: DXLU, DYLU, XCOL, YLIG
        real(kind=4), intent(in), dimension(NSTEPS)       :: DATES
        character(len=13)  , intent(in)              :: TYP_DON
        character(len=132) , intent(in)              :: TITSEM, XFILE
        logical, optional                            :: DEBUG
        !
        !outputs
        integer, intent(out) :: IEREDI
        !
        ! local
        integer :: ISTEP, TMP_ISTEP, NU_ZOO, NU_GRID, N_COUCH, LEC, INVY, NKOL, NLIG, NTOT, NLAY, NGIG, start_idx, end_idx, shift, i
        real :: X0, Y0
        real, dimension(:), allocatable :: XTEMPCOL, YTEMPLIG, DXTEMP, DYTEMP
        real, dimension(:), allocatable :: ZTEMPVAR
        logical :: DEBUGG
        
        INVY   = 0
        IEREDI = 0
        LEC    = 20 ! unité d'écriture, IOUMAI from DTH
        NLAY   = N_DIMS(1, 3)
        NGIG   = NGRID - 1
        DEBUGG = .FALSE.  ! default value for debugging
        !
        IF(PRESENT(DEBUG)) DEBUGG = DEBUG
        !
        OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='write')
        
        ! Starting process:
        ! loop over timesteps, then id_grid (main, gig), then layers. Write each grid.
        ! data are stored in 2D array (Time, Zone), so we need to extract values from it
        ! based on those indexes (layer, grid, time indexes)
        DO ISTEP=1, NSTEPS
            DATE = DATES(ISTEP)
            
            DO NU_GRID=1, NGRID
                
                NU_ZOO = NU_GRID - 1
                NKOL = N_DIMS(NU_GRID, 1)
                NLIG = N_DIMS(NU_GRID, 2)
                
                ! To navigate through ZVAR, before computing start_idx, end_idx based on NLAY, NLIG, NKOL,
                ! we compute a 'shift' index, to jump over previous grids, if id_grid > 0
                ! number of value to skip depends on nlay and nkol, nlig of every previous grid (main, and each gig)
                ! wich might not be equals
                shift = 0
                IF (NU_ZOO >= 1) THEN
                    DO i=NU_ZOO, 1, -1
                        shift = shift + (NLAY * N_DIMS(i, 1) * N_DIMS(i, 2))
                    ENDDO
                ENDIF
                
                
                DO N_COUCH=1, NLAY
                    
                    NTOT = NKOL * NLIG
                    start_idx = ((N_COUCH - 1) * NTOT ) + shift + 1     ! +1 to get 0-based (n-couch -1) to 1-based starting index. if 1st layer return 1 (cause n-couch-1 would be 0)
                    end_idx   = start_idx + NTOT - 1                    ! here minus 1 cause upper bound is included in fortran, would cause error (idx > len)
                    
                    ! Get current var and coords + transf to real 8 for edsemigl
                    ZTEMPVAR = ZVAR(ISTEP, start_idx:end_idx)
                    XTEMPCOL = XCOL(start_idx:start_idx + NKOL - 1)  ! x is repeated for every different y, but EDSEMI_3 will subset to NKOL
                    YTEMPLIG = YLIG(start_idx:end_idx:NKOL)          ! here, same y for each x, so we sample y every nkol (n_x) to get every unique y values, EDSEMI_3 will subset to NLIG
                    DXTEMP   = DXLU(start_idx:start_idx + NKOL - 1)
                    DYTEMP   = DYLU(start_idx:end_idx:NKOL)
                    !
                    X0 = minval(XTEMPCOL) - (DXTEMP(1)/2)                   ! x0 is lowerleft coordinate, xy read are center of cells
                    Y0 = minval(YTEMPLIG) - (DYTEMP(Ubound(DYTEMP, 1))/2)   ! y0 is lowerleft coordinate, xy read are center of cells
                    !
                    ! ISTEP = -9999 is code value for no timestep (eg. used in parameters field)
                    IF (DATE == 0.) THEN
                        TMP_ISTEP = -9999
                    ELSE
                        TMP_ISTEP = ISTEP
                    ENDIF
                    
                    CALL EDSEMI_3(&
                        ZTEMPVAR, NKOL, NLIG, XTEMPCOL, YTEMPLIG, X0, Y0, INVY &
                        ,TITSEM, IEREDI, LEC, TYP_DON &
                        ! //////// Not used now
                        ,TYP_DON3, N_ELEMCH, &
                        ! ////////////////////
                        TMP_ISTEP, N_COUCH, NLAY, NU_ZOO, NGIG, DATE &
                        ! //////// Not used now
                        ,LIBCHIM &
                        ! ////////////////////
                        ,DXTEMP, DYTEMP &
                    )
                    !
                    if (IEREDI /= 0) then
                        if (DEBUGG) then
                            ! errors might come from non-sorted XY or negatives XY
                            write (LEC, *)"Writing error, status ", IEREDI
                            write (LEC, *) "Lay=", N_COUCH, "Grid=", NU_ZOO, "X0=", X0, "Y0=", Y0
                            write (LEC, *) "NCOL=", NKOL, "NLIG=", NLIG, 'NTOT=', NTOT
                            write (LEC, *) "len(X)=", size(XTEMPCOL), "len(Y)=", size(YTEMPLIG), "len(v)", size(ZTEMPVAR)
                            write (LEC, *) 'start_idx=', start_idx, 'end_idx=', end_idx, 'shift_idx=', shift
                            write (LEC, *) 'X: ', XTEMPCOL, ''
                            write (LEC, *) 'Y: ', YTEMPLIG, ''
                            write (LEC, *) 'dx:', DXTEMP, ''
                            write (LEC, *) 'dy:', DYTEMP, ''
                            write (LEC, *) 'v: ', ZTEMPVAR, ''
                        endif
                    endif
                    !
                ENDDO ! end layer loop
            ENDDO ! end grid loop
            !
        ENDDO ! end time loop
        !
        CLOSE(LEC)
        !
    END SUBROUTINE WRITE_GRID
!
END MODULE MODGRIDMARTHE
