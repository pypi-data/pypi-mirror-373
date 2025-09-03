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
!
! (Provenance MARTHE, Fichier : lecsem.f90, convert utf-8 )
!
! MARTHE, Copyright (c) 1990-2024 BRGM
!
      SUBROUTINE LECSEM8_0(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
       , IOUCON, LEC, IERLEC, NUMERR, NTOT &
       , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
!================================================================================
!   ***********
!   *LECSEM8_0*                        BRGM     B.P. 36009
!   ***********                        45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!================================================================================
!        Lecture d'une Grille de points et rangement dans le tableau FONC()
!        Version v7.0 , v8.0 , v9.0
!================================================================================
!     LEC       = Unité de Lecture
!     IOUCON    = Unité Logique d'écriture sur la console    si > 0
!                 Seulement écriture des erreurs sur console si = 0
!                 Pas d'écriture                             si < 0
!     NLIG,NKOL = Nombre maxi de Lignes et de Colonnes (pour XCOL et YLIG)
!     NTOT      = Nombre maxi de places dans le tableau FONC()
!                 N.B. : Si NTOT = 0 => On ne lit pas les points
!                        mais seulement les coordonnées (Il n'y a rien dans FONC)
!     INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
!            : 1 = Inversion la première ligne lue est rangée en dernier
!                  et YLIG est inversé aussi (logiciels d'interpolation)
!     LIRE_DXDY : 0 = On ne veut pas lire de DX() et DY()
!                    (On les saute s'ils existent)
!               : 1 = On veut lire les DX() et DY() (s'ils existent)
!     En Retour :
!     TITSEM = Dernier titre lu pour la Grille (len=132)
!     LU_DXDY : 0 = On n'a pas lu de DX et DY
!             : 1 = On a lu des DX et DY
!     LU_XY   : 0 = On n'a pas lu de X() et Y() : Par ex lecture en format libre
!             : 1 = On a lu des X() et Y()
!     XCOL  = Tableau des abscisses (si LU_XY > 0)
!     YLIG  = Tableau des ordonnées (si LU_XY > 0)
!     DXLU  = DX lus si LU_DXDY > 0
!     DYLU  = DY lus si LU_DXDY > 0
!     NLIG  = Nombre de Lignes
!     NKOL  = Nombre de Colonnes
!     X0    = Abscisse du cote ouest de la colonne n°1    (si LU_XY > 0)
!     Y0    = Ordonnée du    bas     de la ligne   n°NLIG (si LU_XY > 0)
!     NTOT  = Nombre de points = NKOL * NLIG
!     FONC  = Tableau des valeurs lues
!     IERLEC =  0 Si normal
!     IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!     IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!     IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!     IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!================================================================================
      IMPLICIT NONE
      REAL   , DIMENSION(*), INTENT(OUT) :: FONC
      REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
      REAL   , DIMENSION(*) :: DXLU, DYLU
      INTEGER, INTENT(IN)  :: LIRE_DXDY, INVERS, IOUCON, LEC
      INTEGER, INTENT(OUT) :: LU_DXDY, LU_XY, NUMERR, IERLEC
      REAL   , INTENT(IN OUT) :: X0, Y0
      INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
      CHARACTER (LEN=*), INTENT(OUT) :: TITSEM
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=13) :: TYP_DON
      CHARACTER (LEN=7)  :: TYP_DON3
      CHARACTER (LEN=80) :: LIBCHIM
      REAL    :: DATE
      INTEGER :: IANALY, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX
!     =======
!      Début
!     =======
      IANALY = 0
      TITSEM = " "
!     ====================================
!      Appel avec 1 + 9 arguments en plus
!     ====================================
      CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
      END SUBROUTINE LECSEM8_0
      SUBROUTINE LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
!================================================================================
!   **********
!   *LECSEM_3*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!================================================================================
!        Lecture d'une Grille de points et rangement dans le tableau FONC()
!        Version v7.0 , v8.0 , v9.0
!================================================================================
!     LEC       = Unité de Lecture
!     IOUCON    = Unité Logique d'écriture sur la console    si > 0
!                 Seulement écriture des erreurs sur console si = 0
!                 Pas d'écriture                             si < 0
!     NLIG,NKOL = Nombre maxi de Lignes et de Colonnes (pour XCOL et YLIG)
!     NTOT      = Nombre maxi de places dans le tableau FONC()
!                 N.B. : Si NTOT = 0 => On ne lit pas les points,
!                        mais seulement les coordonnées (Il n'y a rien dans FONC)
!     INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
!            : 1 = Inversion la première ligne lue est rangée en dernier
!                  et YLIG est inversé aussi (logiciels d'interpolation)
!     IANALY : 0 = Lecture normale
!            : 1 = Prélecture rapide (pour analyser les dimensions etc)
!                  FONC(), XCOL(), YLIG() ne sont pas valorisés
!                  (N.B. Si binaire => Pas plus rapide)
!     LIRE_DXDY : 0 = On ne veut pas lire de DX et DY
!                    (On les saute s'ils existent)
!               : 1 = On veut lire les DX et DY (s'ils existent)
!     En Retour :
!     TITSEM = Dernier titre lu pour la Grille (len=132)
!     LU_DXDY : 0 = On n'a pas lu de DX et DY
!             : 1 = On a lu des DX et DY
!     XCOL  = Tableau des abscisses (si LU_XY > 0)
!     YLIG  = Tableau des ordonnées (si LU_XY > 0)
!     DXLU  = DX lus si LU_DXDY > 0
!     DYLU  = DY lus si LU_DXDY > 0
!     NLIG  = Nombre de Lignes
!     NKOL  = Nombre de Colonnes
!     X0    = Abscisse du cote ouest de la colonne n°1    (si LU_XY > 0)
!     Y0    = Ordonnée du    bas     de la ligne   n°NLIG (si LU_XY > 0)
!     NTOT  = Nombre de points = NKOL * NLIG
!     FONC  = Tableau des valeurs lues
!      Et aussi
!     TYP_DON  = Type de donnée (len=13)
!     TYP_DON3 = Complément du type de donnée (len=7)
!     N_ELEMCH = Numéro associé au type de donnée (élément Chimique)
!     ISTEP    = Numéro du pas de temps (-9999 si pas lu)
!     N_COUCH  = Numéro de la Couche
!     NCOUC_MX = Nombre maxi de Couches
!     NU_ZOO   = Numéro du Gigogne (0 = Main)
!     NU_ZOOMX = Nombre maxi de Gigognes
!     DATE     = Date associée à la Grille
!     LIBCHIM  = Libellé complémentaire (nom de l'Élément Chimique) (len=80)
!     IERLEC =  0 Si normal
!     IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!     IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!     IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!     IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!================================================================================
      IMPLICIT NONE
      REAL   , DIMENSION(*), INTENT(OUT) :: FONC
      REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
      REAL   , DIMENSION(*) :: DXLU, DYLU
      CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM, LIBCHIM
      CHARACTER (LEN=*), INTENT(OUT) :: TYP_DON
      CHARACTER (LEN=7), INTENT(OUT) :: TYP_DON3
      REAL   , INTENT(OUT)    :: DATE
      REAL   , INTENT(IN OUT) :: X0, Y0
      INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
      INTEGER, INTENT(IN)     :: INVERS, IOUCON, LEC, IANALY
      INTEGER, INTENT(OUT)    :: IERLEC, NUMERR, N_ELEMCH, ISTEP, N_COUCH, NU_ZOO &
                               , NCOUC_MX, NU_ZOOMX
      INTEGER, INTENT(IN)  :: LIRE_DXDY
      INTEGER, INTENT(OUT) :: LU_DXDY, LU_XY
!     ========
!      Locaux
!     ========
      INTEGER :: IERRAUX, I, NONFOR, IPOSIT, ITYP_ARCVIEW
      REAL    :: FMANQ
      CHARACTER (LEN=132) :: TITAUX_MAJUSC
      CHARACTER (LEN=132) :: FIRST_LINE
      CHARACTER (LEN=20) :: TYPFOR
      CHARACTER (LEN=15) :: CHAR15
!     =======
!      Début
!     =======
      LU_DXDY = 0
      LU_XY = 1
      IERLEC = 0
      NUMERR = 0
      I = 0
      TYP_DON  = " "
      TYP_DON3 = " "
      LIBCHIM  = " "
      N_ELEMCH = 0
      ISTEP    = -9999
      N_COUCH  = 1
      NCOUC_MX = 1
      NU_ZOO   = 0
      NU_ZOOMX = 0
      DATE     = 0.
      IF (IANALY > 0) FONC(1) = 0.
!     ================
!      Formaté ou pas
!     ================
      INQUIRE (UNIT=LEC, FORM=TYPFOR)
      NONFOR = 0
      IF (TYPFOR == "UNFORMATTED") NONFOR = 1
      IF (NONFOR == 1) THEN
!        =============
!         Non-formaté
!        =============
         CALL LECSEM_BINARY(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
           , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
           , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
           , LIRE_DXDY, DXLU, DYLU)
         SELECT CASE (IANALY)
         CASE (:0)
            LU_XY = 1
         CASE (1:)
            LU_XY = 0
         END SELECT
         SELECT CASE (LIRE_DXDY)
         CASE (:0)
            LU_DXDY = 0
         CASE (1:)
            LU_DXDY = 1
         END SELECT
!        ====================================
!         Fin de la lecture pour non-formaté
!        ====================================
         GO TO 999
      ENDIF
!     ==================
!      Lecture formatée
!     ==================
!     ======================================================
!      Lecture de la première ligne pour décoder la Version
!     ======================================================
      READ (LEC, "(A)", IOSTAT=IERRAUX) FIRST_LINE
      IF (IERRAUX > 0) GO TO 450
      IF (IERRAUX < 0) GO TO 500
      TITAUX_MAJUSC = TRANSFO_EN_MAJUSC_2(FIRST_LINE)
!     ==========
!      Décodage
!     ==========
      IPOSIT = INDEX(TITAUX_MAJUSC , "MARTHE_GRI")
      IF (IPOSIT > 0) IPOSIT = INDEX(TITAUX_MAJUSC , "VERSION=9.0")
      IF (IPOSIT > 0) THEN
!        ==========================
!         Fichier Marthe_Grid v9.0
!        ==========================
         CALL LECSEM_9_0(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
          , LIRE_DXDY, DXLU, DYLU)
         IF (IERLEC /= 0) GO TO 999
         SELECT CASE (IANALY)
         CASE (:0)
            LU_XY = 1
         CASE (1:)
            LU_XY = 0
         END SELECT
         SELECT CASE (LIRE_DXDY)
         CASE (:0)
            LU_DXDY = 0
         CASE (1:)
            LU_DXDY = 1
         END SELECT
         GO TO 999
      ENDIF
      IF (FIRST_LINE(1:4) == "DSAA") THEN
!        ==================================
!         Fichier [.grd] ASCII de "Surfer"
!        ==================================
         FMANQ = 9999.
         TITSEM = "Grd File : ASCII"
         CALL LESEM_GRD(FONC, X0, Y0, XCOL, YLIG &
                      , NLIG, NKOL, NTOT, LEC, INVERS, FMANQ, DXLU, DYLU &
                      , IERLEC, NUMERR &
                      , IANALY)
         IF (IERLEC /= 0) GO TO 999
         SELECT CASE (IANALY)
         CASE (:0)
            LU_XY = 1
         CASE (1:)
            LU_XY = 0
         END SELECT
         SELECT CASE (LIRE_DXDY)
         CASE (:0)
            LU_DXDY = 0
         CASE (1:)
            LU_DXDY = 1
         END SELECT
         GO TO 999
      ENDIF
      CHAR15 = ADJUSTL(TITAUX_MAJUSC)
      IF (CHAR15(1:6) == "NCOLS ") THEN
!        ===========================================
!         Lecture d'une Grille ASC ASCII de Arcview
!        ===========================================
         FMANQ = 9999.
         TITSEM = "ArcView Asc File : ASCII"
         CALL LESEM_ARCVIEW_ASC(FONC, X0, Y0, XCOL, YLIG &
                     , NLIG, NKOL, NTOT, LEC, INVERS, FMANQ, DXLU, DYLU &
                     , IERLEC, NUMERR &
                     , IANALY, FIRST_LINE, ITYP_ARCVIEW)
         IF (IERLEC /= 0) GO TO 999
         IF (ITYP_ARCVIEW >= 1) THEN
            SELECT CASE (IANALY)
            CASE (:0)
               LU_XY = 1
            CASE (1:)
               LU_XY = 0
            END SELECT
            SELECT CASE (LIRE_DXDY)
            CASE (:0)
               LU_DXDY = 0
            CASE (1:)
               LU_DXDY = 1
            END SELECT
            GO TO 999
         ENDIF
      ENDIF
      IPOSIT = INDEX(FIRST_LINE , "LIBRE")
      IF (IPOSIT == 0) IPOSIT = INDEX(TITAUX_MAJUSC, "LIBRE")
      IF (IPOSIT == 0) IPOSIT = INDEX(TITAUX_MAJUSC, "FREE")
      IF (IPOSIT > 0) THEN
!        =========================================================================
!         Lecture en format Libre tout à la suite, en commençant par la ligne n°1
!        =========================================================================
         TITSEM = "Free format File"
         CALL LESEM_LIBRE(FONC, NTOT, LEC, INVERS &
             ,IERLEC, NUMERR, IANALY)
         LU_XY = 0
         IF (IERLEC /= 0) GO TO 999
         GO TO 999
      ENDIF
!     =========================================
!      Grille format fixe 2.0, 3.0, 7.0 ou 8.0
!     =========================================
      CALL LECSEM_FORMAT_FIXE(FIRST_LINE &
         , X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
         , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
         , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
         , LIRE_DXDY, LU_DXDY, DXLU, DYLU)
         SELECT CASE (IANALY)
         CASE (:0)
            LU_XY = 1
         CASE (1:)
            LU_XY = 0
         END SELECT
      GO TO 999
!     =========
!      Erreurs
!     =========
  450 NUMERR = I
      IERLEC = 1
      GO TO 999
  500 NUMERR = I
      IERLEC = 2
      GO TO 999
  999 CONTINUE
        CONTAINS
        SUBROUTINE LECSEM_9_0(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
               , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
               , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
               , LIRE_DXDY, DXLU, DYLU)
!       ================================================================================
!        ************
!        *LECSEM_9_0*                       BRGM     B.P. 36009
!        ************                       45060 Orléans Cédex
!        Auteur(s):THIERY D.
!        Date: 22/12/2019
!       ================================================================================
!        Lecture d'une Grille de points et rangement dans le tableau FONC()
!        Version 9.0
!       ================================================================================
!         LEC       = Unité de Lecture
!         IOUCON    = Unité Logique d'écriture sur la console    si > 0
!                     Seulement écriture des erreurs sur console si = 0
!                     Pas d'écriture                             si < 0
!         NLIG,NKOL = Nombre maxi de Lignes et de Colonnes (pour XCOL et YLIG)
!         NTOT      = Nombre maxi de places dans le tableau FONC()
!                     N.B. : Si NTOT = 0 => On ne lit pas les points
!                            mais seulement les coordonnées (Il n'y a rien dans FONC)
!         INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
!                : 1 = Inversion la première ligne lue est rangée en dernier
!                      et YLIG est inversé aussi (logiciels d'interpolation)
!         IANALY : 0 = Lecture normale
!                : 1 = Prélecture rapide (pour analyser les dimensions etc)
!                      FONC(), XCOL(), YLIG() ne sont pas valorisés
!                      (N.B. Si binaire => Pas plus rapide)
!         LIRE_DXDY : 0 = On ne veut pas lire de DX et DY
!                        (On les saute s'ils existent)
!                   : 1 = On veut lire les DX et DY (s'ils existent)
!         En Retour :
!         TITSEM = Dernier titre lu pour la Grille (len=132)
!         XCOL  = Tableau des abscisses (si IANALY = 0)
!         YLIG  = Tableau des ordonnées (si IANALY = 0)
!         DXLU  = DX lus si LIRE_DXDY > 0
!         DYLU  = DY lus si LIRE_DXDY > 0
!         NLIG  = Nombre de Lignes
!         NKOL  = Nombre de Colonnes
!         X0    = Abscisse du cote ouest de la colonne n°1
!         Y0    = Ordonnée du    bas     de la ligne   n°NLIG
!         NTOT  = Nombre de points = NKOL * NLIG
!         FONC  = Tableau des valeurs lues
!          Et aussi
!         TYP_DON  = Type de donnée (len=13)
!         TYP_DON3 = Complément du type de donnée (len=7)
!         N_ELEMCH = Numéro associé au type de donnée (élément Chimique)
!         ISTEP    = Numéro du pas de temps (-9999 si pas lu)
!         N_COUCH  = Numéro de la Couche
!         NCOUC_MX = Nombre maxi de Couches
!         NU_ZOO   = Numéro du Gigogne (0 = Main)
!         NU_ZOOMX = Nombre maxi de Gigognes
!         DATE     = Date associée à la Grille
!         LIBCHIM  = Libellé complémentaire (nom de l'Élément Chimique) (len=80)
!         IERLEC =  0 Si normal
!         IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!         IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!         IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!         IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!       ================================================================================
        IMPLICIT NONE
        REAL   , DIMENSION(*), INTENT(OUT) :: FONC
        REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
        REAL   , DIMENSION(*) :: DXLU, DYLU
        CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM, LIBCHIM
        CHARACTER (LEN=*), INTENT(IN OUT) :: TYP_DON
        CHARACTER (LEN=7), INTENT(IN OUT) :: TYP_DON3
        REAL   , INTENT(IN OUT) :: DATE
        REAL   , INTENT(IN OUT) :: X0, Y0
        INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
        INTEGER, INTENT(IN)     :: INVERS, IOUCON, LEC, IANALY
        INTEGER, INTENT(IN OUT) :: IERLEC, NUMERR, N_ELEMCH, ISTEP, N_COUCH, NU_ZOO &
                                 , NCOUC_MX, NU_ZOOMX
        INTEGER, INTENT(IN)     :: LIRE_DXDY
!       ========
!        Locaux
!       ========
        INTEGER :: I, K, L, IERRAUX, IAUX1, IAUX2, LIG, NEED, NKOLMA, NLIGMA, IPOSIT &
                 , IOUCAUX, IGRID_CONST, LIGAUX, IND1
        REAL    :: VALEUR
        CHARACTER (LEN=132) :: TITR132, TITAUX_MAJUSC
        CHARACTER (LEN=30)  :: CHAR30
        REAL   , DIMENSION(9999) :: TABAUX
!       =======
!        Début
!       =======
        IF (IANALY == 0) THEN
           NKOLMA = NKOL
           NLIGMA = NLIG
        ENDIF
        I   = 0
        LIG = 0
        IOUCAUX = IOUCON
        IF (IOUCAUX <= 0) IOUCAUX = 6
!       ==================================
!        Lecture du titre :
!        Title = Substratum Nappe Exemple
!       ==================================
        READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
        IF (IERRAUX < 0) GO TO 500
        IPOSIT = INDEX(TITR132 , "=")
        TITR132 = TITR132(IPOSIT+1:)
        DO K=1,LEN(TITR132)
           IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
           IF (TITR132(K:K) == ACHAR(9)) TITR132(K:K) = " "
        ENDDO
        TITSEM = TITR132
!       =================
!        [Infos]
!        Field=CONCENTR
!        Type=Liq
!        Elem_Number=1
!        Name=-total_h
!        Time_Step=0
!        Time=0.00E+00
!        Layer=1
!        Max_Layer=1
!        Nest_grid=0
!        Max_NestG=0
!       =================
        READ (LEC, *, IOSTAT=IERRAUX)
        IF (IERRAUX < 0) GO TO 500
!       ============================================
!        ISTEP = -9999 => Code que pas d'infos lues
!       ============================================
        DO L=1,10
           READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
           IF (IERRAUX < 0) GO TO 500
           IPOSIT = INDEX(TITR132 , "=")
           TITR132 = TITR132(IPOSIT+1:)
           SELECT CASE (L)
           CASE (1 , 2 , 4)
              DO K=1,LEN(TITR132)
                 IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
                 IF (TITR132(K:K) == ACHAR(9)) TITR132(K:K) = " "
              ENDDO
           END SELECT
           IERRAUX = 0
           SELECT CASE (L)
           CASE (1)
              TYP_DON = TITR132
           CASE (2)
              TYP_DON3 = TITR132
           CASE (3)
              READ (TITR132 , * , IOSTAT=IERRAUX) N_ELEMCH
           CASE (4)
              LIBCHIM = TITR132
              LIBCHIM = ADJUSTL(LIBCHIM)
           CASE (5)
              READ (TITR132, *, IOSTAT=IERRAUX) ISTEP
           CASE (6)
              READ (TITR132, *, IOSTAT=IERRAUX) DATE
           CASE (7)
              READ (TITR132, *, IOSTAT=IERRAUX) N_COUCH
           CASE (8)
              READ (TITR132, *, IOSTAT=IERRAUX) NCOUC_MX
           CASE (9)
              READ (TITR132, *, IOSTAT=IERRAUX) NU_ZOO
           CASE (10)
              READ (TITR132, *, IOSTAT=IERRAUX) NU_ZOOMX
           END SELECT
!          ============================================
!           ISTEP = -9999 => Code que pas d'infos lues
!          ============================================
           IF (IERRAUX /= 0) ISTEP = -9999
        ENDDO
!       ====================
!        [Structure]
!        X_Left_Corner=200
!        Y_Lower_Corner=300
!        Ncolumn=20
!        Nrows=30
!       ====================
        READ (LEC, *, IOSTAT=IERRAUX)
        IF (IERRAUX < 0) GO TO 500
        DO L=1,4
           READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
           IF (IERRAUX < 0) GO TO 500
           IPOSIT = INDEX(TITR132 , "=")
           TITR132 = TITR132(IPOSIT+1:)
           SELECT CASE (L)
           CASE (1)
              READ (TITR132, *, IOSTAT=IERRAUX) X0
           CASE (2)
              READ (TITR132, *, IOSTAT=IERRAUX) Y0
           CASE (3)
              READ (TITR132, *, IOSTAT=IERRAUX) NKOL
           CASE (4)
              READ (TITR132, *, IOSTAT=IERRAUX) NLIG
           END SELECT
           IF (IERRAUX /= 0) GO TO 450
        ENDDO
        IF ((NLIG <= 0).OR.(NKOL <= 0)) THEN
           IERLEC = -1
           GO TO 999
        ENDIF
        NEED = NLIG * NKOL
        SELECT CASE (IANALY)
        CASE (0)
           IF ( (NLIG > NLIGMA).OR.(NKOL > NKOLMA).OR. &
                ((NEED > NTOT).AND.(NTOT /= 0)) ) THEN
              NKOL = NKOLMA
              NLIG = NLIGMA
              IERLEC = 3
              GO TO 999
           ENDIF
        CASE (1:)
           NTOT = NLIG * NKOL
        END SELECT
!       =============================
!        Pas d'erreurs de dimensions
!       =============================
        IF (NTOT > 0) NTOT = NEED
        SELECT CASE (IANALY)
        CASE (1:)
!          ==============================================================================
!           Analyse seule : Rien : On ne récupère pas les XCOL, YLIG, DXLU, DYLU ni FONC
!          ==============================================================================
           DO WHILE (.TRUE.)
              READ (LEC, "(A)" , IOSTAT=IERRAUX) CHAR30
              IF (IERRAUX < 0) GO TO 999
              TITAUX_MAJUSC = TRANSFO_EN_MAJUSC_2(CHAR30)
              IF (INDEX( TITAUX_MAJUSC , "[END_GRID]") > 0) GO TO 999
           ENDDO
        END SELECT
!       ==================================
!        On a traité le cas de IANALY = 1
!        => À partir d'ici : ANALY = 0
!       ==================================
        I = 0
!       ==================================================
!        [Data]  ou  [Data_Descript]  ou  [Constant_Data]
!       ==================================================
        READ (LEC, "(A)" , IOSTAT=IERRAUX) TITR132
        IF (IERRAUX < 0) GO TO 500
        TITAUX_MAJUSC = TRANSFO_EN_MAJUSC_2(TITR132)
        IPOSIT = INDEX(TITAUX_MAJUSC , "CONSTANT_DATA")
        IF (IPOSIT > 0) THEN
           IGRID_CONST = 1
        ELSE
           IGRID_CONST = 0
        ENDIF
        SELECT CASE (IGRID_CONST)
        CASE (0)
!          ==================================
!           Cas général Grille non constante
!          ==================================
           IPOSIT = INDEX(TITAUX_MAJUSC , "DATA_DESCRIPT")
           IF (IPOSIT > 0) THEN
!             =========================================================================================
!              6 lignes de descriptions à sauter
!              ! Line 1       :   0   ,     0          , <   1 , 2 , 3 , Ncolumn   >
!              ! Line 2       :   0   ,     0          , < X_Center_of_all_Columns >
!              ! Line 3       :   1   , Y_of_Row_1     , < Field_Values_of_all_Columns > , Dy_of_Row_1
!              ! Line 4       :   2   , Y_of_Row_2     , < Field_Values_of_all_Columns > , Dy_of_Row_2
!              ! Line 2+Nrows : Nrows , Y_of_Row_Nrows , < Field_Values_of_all_Columns > , Dy_of_Row_2
!              ! Line 3+Nrows :   0   ,     0          , <     Dx_of_all_Columns   >
!             =========================================================================================
              DO WHILE (.TRUE.)
                 READ (LEC, "(A)" , IOSTAT=IERRAUX) TITR132
                 IF (IERRAUX < 0) GO TO 500
                 TITAUX_MAJUSC = TRANSFO_EN_MAJUSC_2(TITR132)
                 IPOSIT = INDEX(TITAUX_MAJUSC , "[DATA")
                 IF (IPOSIT > 0) EXIT
              ENDDO
           ENDIF
!          ============================================================================
!           Lecture des valeurs
!          ============================================================================
!           Ligne n°1  : Numéros de colonne
!           Ligne n°2  : 0 , 0 , XCOL(1:NKOL)
!           Lignes n°2+1 à NLIG+2 : Num , YLIG(ligaux) , TABAUX(1:NKOL) , DYLU(ligaux)
!           Ligne Last : 0 , 0 , DXLU(1:NKOL)
!          ============================================================================
           READ (LEC, *, IOSTAT=IERRAUX)
           IF (IERRAUX < 0) GO TO 500
           READ (LEC, *, IOSTAT=IERRAUX) IAUX1, IAUX2, XCOL(1:NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           DO LIG=1,NLIG
              LIGAUX = MERGE( LIG , NLIG-LIG+1 , (INVERS == 0) )
              IND1 = (LIGAUX - 1) * NKOL
              SELECT CASE (LIRE_DXDY)
              CASE (1:)
                 READ (LEC, *, IOSTAT=IERRAUX) IAUX1 , YLIG(LIGAUX) , TABAUX(1:NKOL) , DYLU(LIGAUX)
              CASE (:0)
                 READ (LEC, *, IOSTAT=IERRAUX) IAUX1 , YLIG(LIGAUX) , TABAUX(1:NKOL)
              END SELECT
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              IF (NTOT > 0) THEN
                 FONC(IND1+1:IND1+NKOL) = TABAUX(1:NKOL)
              ENDIF
           ENDDO
           SELECT CASE (LIRE_DXDY)
           CASE (1:)
              READ (LEC, *, IOSTAT=IERRAUX) IAUX1, IAUX2, DXLU(1:NKOL)
           CASE (:0)
              READ (LEC, *, IOSTAT=IERRAUX)
           END SELECT
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
        CASE (1)
!          =====================================
!           Grille constante
!           Lecture des valeurs
!          =====================================
!           Ligne n°1  : Uniform_Value=1.00000
!           Ligne n°2  : [Num_Columns_/_x_/_dx]
!           Ligne n°3  : Numéros de colonne
!           Ligne n°4  : XCOL(1:NKOL)
!           Ligne n°5  : DXLU(1:NKOL)
!           Ligne n°6  : [Num_Rows_/_y_/_dy]
!           Ligne n°7  : Numéros de ligne
!           Ligne n°8  : YLIG(1:NLIG)
!           Ligne n°9  : DYLU(1:NLIG)
!          =====================================
           LIG = 999
           READ (LEC, "(A)" , IOSTAT=IERRAUX) TITR132
           IF (IERRAUX < 0) GO TO 500
           IPOSIT = INDEX(TITR132 , "=")
           TITR132 = TITR132(IPOSIT+1:)
           READ (TITR132 , * , IOSTAT=IERRAUX) VALEUR
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           IF (NTOT > 0) FONC(1:NTOT) = VALEUR
!          ========================
!           [Num_Columns_/_x_/_dx]
!          ========================
           READ (LEC, *, IOSTAT=IERRAUX)
           IF (IERRAUX < 0) GO TO 500
!          ==============
!           Num colonnes
!          ==============
           READ (LEC, *, IOSTAT=IERRAUX)
           IF (IERRAUX < 0) GO TO 500
           READ (LEC, *, IOSTAT=IERRAUX) XCOL(1:NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           SELECT CASE (LIRE_DXDY)
           CASE (1:)
              READ (LEC, *, IOSTAT=IERRAUX) DXLU(1:NKOL)
           CASE (:0)
              READ (LEC, *, IOSTAT=IERRAUX)
           END SELECT
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
!          =====================
!           [Num_Rows_/_y_/_dy]
!          =====================
           READ (LEC, *, IOSTAT=IERRAUX)
           IF (IERRAUX < 0) GO TO 500
!          ============
!           Num Lignes
!          ============
           READ (LEC, *, IOSTAT=IERRAUX)
           IF (IERRAUX < 0) GO TO 500
           SELECT CASE (INVERS)
           CASE (0)
              READ (LEC, *, IOSTAT=IERRAUX) YLIG(1:NLIG)
           CASE DEFAULT
              READ (LEC, *, IOSTAT=IERRAUX) YLIG(NLIG:1:-1)
           END SELECT
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           SELECT CASE (LIRE_DXDY)
           CASE (1:)
              SELECT CASE (INVERS)
              CASE (0)
                 READ (LEC, *, IOSTAT=IERRAUX) DYLU(1:NLIG)
              CASE DEFAULT
                 READ (LEC, *, IOSTAT=IERRAUX) DYLU(NLIG:1:-1)
              END SELECT
           CASE (:0)
              READ (LEC, *, IOSTAT=IERRAUX)
           END SELECT
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
        END SELECT
!       ============
!        [End_Grid]
!       ============
        READ (LEC, *, IOSTAT=IERRAUX)
        IF (IERRAUX < 0) GO TO 500
        GO TO 999
!       =========
!        Erreurs
!       =========
    450 NUMERR = I
        IERLEC = 1
        GO TO 999
    500 NUMERR = I
        IERLEC = 2
        GO TO 999
    999 CONTINUE
   9006 FORMAT (" ***********************************************************" &
               /" * Sous-dimensionnement dans la lecture de Grille",T60,"*" &
               /" * Nb Lignes  = ",I0," (Maxi prévu: ",I0,")" &
               /" * Nb Colonnes= ",I0," (Maxi prévu: ",I0,")" &
               /" * Nb Points  = ",I0," (Maxi prévu: ",I0,")" &
               /" *              Fin d'exécution probable",T60,"*" &
               /" ***********************************************************")
   9008 FORMAT (/" ** Erreur de lecture, ligne n°",I0," **")
        END SUBROUTINE LECSEM_9_0
        SUBROUTINE LECSEM_BINARY(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
          , LIRE_DXDY, DXLU, DYLU)
!       =======================================================================
!          ***************
!          *LECSEM_BINARY*                    BRGM     B.P. 36009
!          ***************                    45060 Orléans Cédex
!          Auteur(s):THIERY D.
!          Date: 22/12/2019
!       =======================================================================
!               Lecture Binaire : Non Formaté
!       =======================================================================
        IMPLICIT NONE
        REAL   , DIMENSION(*), INTENT(OUT) :: FONC
        REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
        REAL   , DIMENSION(*) :: DXLU, DYLU
        CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM, LIBCHIM
        CHARACTER (LEN=*), INTENT(IN OUT) :: TYP_DON
        CHARACTER (LEN=7), INTENT(IN OUT) :: TYP_DON3
        REAL   , INTENT(IN OUT) :: DATE
        REAL   , INTENT(IN OUT) :: X0, Y0
        INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
        INTEGER, INTENT(IN)     :: INVERS, IOUCON, LEC, IANALY
        INTEGER, INTENT(IN OUT) :: IERLEC, NUMERR, N_ELEMCH, ISTEP, N_COUCH, NU_ZOO &
                                 , NCOUC_MX, NU_ZOOMX
        INTEGER, INTENT(IN)     :: LIRE_DXDY
!       ========
!        Locaux
!       ========
        INTEGER :: I, K, IERRAUX, LONAUX, IDBAUX, NEED, IND1, LIG, NKOLMA, NLIGMA, IOUCAUX, IAUX1, IAUX2
        REAL    :: XFICT, YFICT, VALEUR, AUXI1, AUXI2, FICT
        CHARACTER (LEN=1)  :: EGALIT
        CHARACTER (LEN=8)  :: BINARY
        CHARACTER (LEN=80) :: LIBCHIM80
        CHARACTER (LEN=132) :: TITR132
!       =======
!        Début
!       =======
        NKOLMA = NKOL
        NLIGMA = NLIG
        IOUCAUX = IOUCON
        IF (IOUCAUX <= 0) IOUCAUX = 6
        I = 0
        READ (LEC, IOSTAT=IERRAUX) BINARY
        IF (IERRAUX > 0) GO TO 450
        IF (IERRAUX < 0) GO TO 500
        READ (LEC, IOSTAT=IERRAUX) TITR132
        IF (IERRAUX > 0) GO TO 450
        IF (IERRAUX < 0) GO TO 500
        DO K=1,LEN(TITR132)
           IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
           IF (TITR132(K:K) == ACHAR(9)) TITR132(K:K) = " "
        ENDDO
        TITSEM = TITR132
        LONAUX = LEN_TRIM(TITR132(72:90))
        IF (LONAUX > 0) THEN
!          ======================================================
!           Les infos (Code + n°) peuvent dépasser 79 caractères
!          ======================================================
           IDBAUX = 79 - LONAUX
           TITSEM(IDBAUX:IDBAUX) = " "
           TITSEM(IDBAUX+1:IDBAUX+LONAUX) = TITR132(71+1:71+LONAUX)
        ENDIF
        READ (LEC, IOSTAT=IERRAUX) NKOL, NLIG, X0, Y0
        IF (IERRAUX > 0) GO TO 450
        IF (IERRAUX < 0) GO TO 500
        SELECT CASE (IANALY)
        CASE (1:)
           NTOT = NLIG * NKOL
        CASE (0)
           IF ((NLIG <= 0).OR.(NKOL <= 0)) THEN
              IERLEC = -1
              GO TO 999
           ENDIF
           NEED = NLIG * NKOL
           IF ((NLIG > NLIGMA).OR.(NKOL > NKOLMA).OR. &
               ((NEED > NTOT).AND.(NTOT /= 0)) ) THEN
              NKOL = NKOLMA
              NLIG = NLIGMA
              IERLEC = 3
              GO TO 999
           ENDIF
        END SELECT
        IF (NTOT > 0) NTOT = NEED
        SELECT CASE ( BINARY(1:8) )
        CASE ("#BINAR2#" , "#BINAR3#")
!          ================================
!           Informations supplémentaires
!           (Placées après NKOL, NLIG etc)
!          ================================
           READ (LEC, IOSTAT=IERRAUX) TYP_DON, TYP_DON3, N_ELEMCH, ISTEP &
             , N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, IAUX1, IAUX2, AUXI1, AUXI2
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           IF (BINARY(1:8) == "#BINAR3#") THEN
!             =======================================================
!              Libellé complémentaire
!              On lit 80 caractères obligatoirement : donc LIBCHIM80
!             =======================================================
              READ (LEC, IOSTAT=IERRAUX) LIBCHIM80
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              LIBCHIM = TRIM(LIBCHIM80)
              LIBCHIM = ADJUSTL(LIBCHIM)
           ENDIF
        END SELECT
        SELECT CASE (IANALY)
        CASE (0)
           READ (LEC, IOSTAT=IERRAUX) XCOL(1:NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           SELECT CASE (INVERS)
           CASE (:0)
              READ (LEC, IOSTAT=IERRAUX) YLIG(1:NLIG)
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           CASE DEFAULT
!             ============
!              INVERS = 1
!             ============
              READ (LEC, IOSTAT=IERRAUX) YLIG(NLIG:1:-1)
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           END SELECT
        CASE (1:)
!          ===============
!           Analyse seule
!          ===============
           READ (LEC, IOSTAT=IERRAUX) (XFICT, K=1,NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           READ (LEC, IOSTAT=IERRAUX) (YFICT, K=1,NLIG)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
        END SELECT
        READ (LEC, IOSTAT=IERRAUX) EGALIT
        IF (IERRAUX > 0) GO TO 450
        IF (IERRAUX < 0) GO TO 500
        IF (EGALIT == "=") THEN
!          ==================
!           Grille constante
!          ==================
           READ (LEC, IOSTAT=IERRAUX) VALEUR
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           IF ((NTOT > 0).AND.(IANALY == 0)) FONC(1:NTOT) = VALEUR
        ELSE
!          ====================================
!           Cas général : Grille non constante
!          ====================================
           SELECT CASE (IANALY)
           CASE (0)
              DO LIG=1,NLIG
                 IND1 = MERGE( (LIG-1)*NKOL , (NLIG-LIG)*NKOL , (INVERS <= 0) )
                 READ (LEC, IOSTAT=IERRAUX) FONC(IND1+1:IND1+NKOL)
                 IF (IERRAUX > 0) GO TO 450
                 IF (IERRAUX < 0) GO TO 500
              ENDDO
           CASE (1:)
!             ===============
!              Analyse seule
!             ===============
              DO LIG=1,NLIG
                 READ (LEC, IOSTAT=IERRAUX) (FICT, K=1,NKOL)
                 IF (IERRAUX > 0) GO TO 450
                 IF (IERRAUX < 0) GO TO 500
              ENDDO
           END SELECT
        ENDIF
        IF (LIRE_DXDY > 0) THEN
!          =======================================================================
!           Lecture des DX() et DY()
!           Comme ici : On lit toujours DX() et DY()
!                       Car le binaire n'est pas conçu pour se conserver ...
!                       On suppose donc que binaire récent donc avec DX() et DY()
!          =======================================================================
           READ (LEC, IOSTAT=IERRAUX) DXLU(1:NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           SELECT CASE (INVERS)
           CASE (:0)
              READ (LEC, IOSTAT=IERRAUX) DYLU(1:NLIG)
           CASE DEFAULT
!             =================
!              INVERS = 1 ou 2
!             =================
              READ (LEC, IOSTAT=IERRAUX) DYLU(NLIG:1:-1)
           END SELECT
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           IF ((ALL( DYLU(1:NLIG) > 0.)).AND. &
               (ALL( DXLU(1:NKOL) > 0.))) THEN
!             =========================================================================
!              Recalcul des XCOL() et YLIG() à partir des DXLU(), DYLU() (plus précis)
!             =========================================================================
              CALL DXDY_XCOLYLIG( DXLU, DYLU, XCOL, YLIG, X0, Y0, NLIG, NKOL, INVERS )
           ENDIF
        ELSE
!          =================================
!           Saute les lignes des DX(), DY()
!          =================================
           READ (LEC, IOSTAT=IERRAUX) (FICT, K=1,NKOL)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           READ (LEC, IOSTAT=IERRAUX) (FICT, K=1,NLIG)
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
        ENDIF
!       ====================================
!        Fin de la lecture pour non-formaté
!       ====================================
        GO TO 999
!       =========
!        Erreurs
!       =========
    450 NUMERR = I
        IERLEC = 1
        GO TO 999
    500 NUMERR = I
        IERLEC = 2
        GO TO 999
    999 CONTINUE
   9006 FORMAT (" ***********************************************************" &
               /" * Sous-dimensionnement dans la lecture de Grille",T60,"*" &
               /" * Nb Lignes  = ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" * Nb Colonnes= ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" * Nb Points  = ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" *              Fin d'exécution probable",T60,"*" &
               /" ***********************************************************")
   9007 FORMAT (" *** Fin normale de la lecture de cette Grille ***")
   9008 FORMAT (/" ** Erreur de lecture, ligne n°",I0," **")
        END SUBROUTINE LECSEM_BINARY
        SUBROUTINE DXDY_XCOLYLIG( DXLU, DYLU, XCOL, YLIG, X0, Y0, NLIG, NKOL, INVERS )
!       =================================================
!        Calcul des XCOL et YLIG à partir des DXLU, DYLU
!       =================================================
        IMPLICIT NONE
        INTEGER, INTENT(IN) :: NLIG, NKOL, INVERS
        REAL   , INTENT(IN) :: X0, Y0
        REAL   , DIMENSION(NKOL), INTENT(IN)  :: DXLU
        REAL   , DIMENSION(NLIG), INTENT(IN)  :: DYLU
        REAL   , DIMENSION(NKOL), INTENT(OUT) :: XCOL
        REAL   , DIMENSION(NLIG), INTENT(OUT) :: YLIG
!       ========
!        Locaux
!       ========
        INTEGER :: KOL, LIG, LIGAUX
        REAL    :: X_END, Y_END, DXP2, DYP2, DX2, DY2
!       =======
!        Début
!       =======
!       ===========
!        Abscisses
!       ===========
        X_END = X0
        DXP2  = 0.
        DO KOL=1,NKOL
           DX2       = 0.5 * DXLU(KOL)
           X_END     = X_END + DXP2 + DX2
           XCOL(KOL) = X_END
           DXP2      = DX2
        ENDDO
!       ===========
!        Ordonnées
!       ===========
        Y_END = Y0 + SUM( DYLU(1:NLIG) )
        DYP2  = 0.
        DO LIGAUX=1,NLIG
           IF (INVERS == 1) THEN
              LIG = NLIG - LIGAUX + 1
           ELSE
              LIG = LIGAUX
           ENDIF
           DY2       = 0.5 * DYLU(LIG)
           Y_END     = Y_END - DYP2 - DY2
           YLIG(LIG) = Y_END
           DYP2      = DY2
        ENDDO
        END SUBROUTINE DXDY_XCOLYLIG
        SUBROUTINE LECSEM_FORMAT_FIXE(FIRST_LINE &
          , X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT, IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, DXLU, DYLU)
!       ==================================================================================
!        ********************
!        *LECSEM_FORMAT_FIXE*               BRGM     B.P. 36009
!        ********************               45060 Orléans Cédex
!        Auteur(s):THIERY D.
!        Date: 22/12/2019
!       ==================================================================================
!             Lecture d'une Grille de points et rangement dans le tableau FONC()
!             Format Fixe : Versions 2.0, 3.0, 7.0 ou 8.0
!        TYPE = <CHARG>/LIB/12345; STEP=1234567; LAY=1234/1234; Nest=12/12; T= 1.2345E123
!        TYPE = <CHARG>/LIB/12345; STEP=1234567; LAY=1234/1234; Nest=12/12; T= 1.2345E123
!        Name = Calcite ;
!       ==================================================================================
        IMPLICIT NONE
        CHARACTER (LEN=*), INTENT(IN) :: FIRST_LINE
        REAL   , DIMENSION(*), INTENT(OUT) :: FONC
        REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
        REAL   , DIMENSION(*) :: DXLU, DYLU
        CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM, LIBCHIM
        CHARACTER (LEN=*), INTENT(IN OUT) :: TYP_DON
        CHARACTER (LEN=7), INTENT(IN OUT) :: TYP_DON3
        REAL   , INTENT(IN OUT) :: DATE
        REAL   , INTENT(IN OUT) :: X0, Y0
        INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
        INTEGER, INTENT(IN)     :: INVERS, IOUCON, LEC, IANALY
        INTEGER, INTENT(IN OUT) :: IERLEC, NUMERR, N_ELEMCH, ISTEP, N_COUCH, NU_ZOO &
                                 , NCOUC_MX, NU_ZOOMX
        INTEGER, INTENT(IN)     :: LIRE_DXDY
        INTEGER, INTENT(IN OUT) :: LU_DXDY
!       ========
!        Locaux
!       ========
        INTEGER :: IDBAUX, LONAUX
        INTEGER :: NBLIG_A_LIRE, IERRAUX, IERR, IDEB, IFIN, IOUCAUX, I, K, IPANN &
                 , NEED, NLIGP, NKOLP, NKOLMA, NLIGMA, IPAS, LIG, LIGAUX &
                 , IND1, INDPAN, KONT, NPANN, IPOSIT, LONGTIT, NBREEL &
                 , IEXIS_DX
        REAL    :: VALEUR
        REAL    :: X0_PRECIS, Y0_PRECIS
        REAL   , DIMENSION(10) :: TABAUX
        CHARACTER (LEN=7),  DIMENSION(10) :: TABCHAR7
        CHARACTER (LEN=12), DIMENSION(12) :: TABCHAR12
        CHARACTER (LEN=10) :: CHAR10
        CHARACTER (LEN=12) :: CHAR12
        CHARACTER (LEN=1)  :: EGALIT, PANN_EGA
        CHARACTER (LEN=7)  :: VERSIO = " "
        CHARACTER (LEN=132) :: TITR132, TITAUX
        CHARACTER (LEN=15)  :: CHAR15
!       =======
!        Début
!       =======
        IF (IANALY == 0) THEN
           NKOLMA = NKOL
           NLIGMA = NLIG
        ENDIF
        IOUCAUX = IOUCON
        IF (IOUCAUX <= 0) IOUCAUX = 6
        NPANN = 9999
        I   = 0
        LIG = 0
        EGALIT = " "
        IPANN  = 1
        TITSEM = " "
        BAL_PANN: DO IPANN=1,9999
           IF (IPANN > NPANN) EXIT BAL_PANN
           IF ((IPANN == 1).OR.(EGALIT == " ")) THEN
!             ===============================================
!              Donc pas lecture si IPANN > 1 et EGALIT = "="
!             ===============================================
              SELECT CASE (IPANN)
              CASE (:1)
!                ==========================================================
!                 Premier panneau : On a déjà lu la ligne n°1 : FIRST_LINE
!                ==========================================================
                 TITAUX = FIRST_LINE
              CASE (2:)
                 READ (LEC, "(A)", IOSTAT=IERRAUX) TITAUX
                 IF (IERRAUX > 0) GO TO 450
                 IF (IERRAUX < 0) GO TO 500
              END SELECT
              READ (TITAUX,"(T27,A3)", IOSTAT=IERRAUX) VERSIO
              SELECT CASE (VERSIO)
              CASE ("8.0")
!                =============================
!                 Version 8.0 (12 caractères)
!                =============================
                 READ (TITAUX,9011, IOSTAT=IERRAUX) PANN_EGA, NPANN, VERSIO, EGALIT &
                  , NLIG, NKOL, X0, Y0
              CASE DEFAULT
                 READ (TITAUX,9005, IOSTAT=IERRAUX) PANN_EGA, NPANN, VERSIO, EGALIT &
                  , NLIG, NKOL, X0, Y0
              END SELECT
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           ENDIF
           IF ((NPANN <= 0).OR.(NLIG <= 0).OR.(NKOL <= 0)) GO TO 520
           IF ( (IPANN > 1).AND. &
                ((NLIG /= NLIGP).OR.(NKOL /= NKOLP)) ) THEN
!             ============================
!              Incohérence dans la Grille
!             ============================
              IERLEC = 3
              GO TO 999
           ENDIF
           NLIGP = NLIG
           NKOLP = NKOL
           NEED = NLIG * NKOL
           SELECT CASE (IANALY)
           CASE (0)
              IF ( (NLIG > NLIGMA).OR.(NKOL > NKOLMA).OR. &
                   ((NEED > NTOT).AND.(NTOT /= 0)) ) THEN
                 NKOL = NKOLMA
                 NLIG = NLIGMA
                 IERLEC = 3
                 GO TO 999
              ENDIF
           CASE (1:)
              NTOT = NLIG * NKOL
           END SELECT
!          ===============================================
!           Pas d'erreurs de dimensions ni d'incohérences
!          ===============================================
!          =======================================================
!           Saute les lignes éventuelles précedées par "!" ou "#"
!           situées avant le titre
!          =======================================================
           KONT = 0
           TITR132 = " "
           TITR132(1:1) = "!"
           DO WHILE (.TRUE.)
              READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              TITAUX = ADJUSTL(TITR132)
              IF ((TITAUX(1:1) /= "!").AND.(TITAUX(1:1) /= "#")) EXIT
              KONT = KONT + 1
              IF ( (KONT == 1).AND. &
                  ((TITAUX(1:1) == "!").OR.(TITAUX(1:1) == "#")) ) THEN
!                ============================================
!                 Essai de lecture des infos complémentaires
!                ============================================
                 CALL LESEMI_Lit_Info_Complem(TITR132, TYP_DON, TYP_DON3, DATE &
                     , N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                     , IERR)
                 IF (IERR /= 0) THEN
!                   =================================================
!                    Si erreur (IERR) => Pas grave => Infos pas lues
!                   =================================================
                    ISTEP = -9999
                 ENDIF
              ENDIF
              IF ( (KONT == 2).AND. &
                  ((TITAUX(1:1) == "!").OR.(TITAUX(1:1) == "#")) ) THEN
!                ==============================================
!                 Essai de lecture d'un libellé complémentaire
!                 Décodage : à partir de "=" ou ":"
!                ==============================================
                 LIBCHIM = " "
                 IPOSIT = INDEX(TITR132,":")
                 IF (IPOSIT == 0) IPOSIT = INDEX(TITR132, "=")
                 IF (IPOSIT == 0) IPOSIT = 2
                 LONGTIT = LEN_TRIM(TITR132)
                 LIBCHIM = TITR132(IPOSIT+1:LONGTIT)
                 LIBCHIM = ADJUSTL(LIBCHIM)
              ENDIF
           ENDDO
           IF (NTOT > 0) NTOT = NEED
           INDPAN = (IPANN - 1) * 10
           IDEB   = INDPAN + 1
           IFIN   = INDPAN + 10
           IF (IFIN > NKOL) IFIN = NKOL
           NBREEL = IFIN - IDEB + 1
           I = 0
           IF ((IPANN == 1).AND.(EGALIT == "=")) THEN
!             ================================================================
!              Grille Constante (Premier Panneau) : TITR132 contient le titre
!             ================================================================
              DO K=1,LEN(TITR132)
                 IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
                 IF (TITR132(K:K) == ACHAR(9)) TITR132(K:K) = " "
              ENDDO
              TITSEM = TITR132
              LONAUX = LEN_TRIM(TITR132(72:90))
              IF (LONAUX > 0) THEN
!                ======================================================
!                 Les infos (Code + n°) peuvent dépasser 79 caractères
!                ======================================================
                 IDBAUX = 79 - LONAUX
                 TITSEM(IDBAUX:IDBAUX) = " "
                 TITSEM(IDBAUX+1:IDBAUX+LONAUX) = TITR132(71+1:71+LONAUX)
              ENDIF
!             ============================================================
!              Lecture d'une Ligne pour lire les XCOL (dans le Character)
!             ============================================================
              READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           ENDIF
           SELECT CASE (IANALY)
           CASE (0)
!             ========================================
!              Lecture des XCOL qui sont dans TITR132
!             ========================================
              SELECT CASE (VERSIO)
              CASE ("8.0")
                 READ (TITR132, "(11F12.0)", IOSTAT=IERRAUX) XCOL(IDEB:IFIN)
              CASE DEFAULT
                 READ (TITR132, "(10F7.0,F10.0)", IOSTAT=IERRAUX) XCOL(IDEB:IFIN)
              END SELECT
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           CASE (1:)
!             ======================================================
!              Analyse seule : Rien : On ne récupère pas les XCOL()
!             ======================================================
           END SELECT
           I = 0
           SELECT CASE (EGALIT)
           CASE (" ")
!             =====================================================================
!              Cas général : Grille non constante : Lecture du titre à chaque fois
!             =====================================================================
              READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
              IF (IERRAUX < 0) GO TO 500
              DO K=1,LEN(TITR132)
                 IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
                 IF (TITR132(K:K) == ACHAR(9)) TITR132(K:K) = " "
              ENDDO
              TITSEM = TITR132
              LONAUX = LEN_TRIM(TITR132(72:90))
              IF (LONAUX > 0) THEN
!                ======================================================
!                 Les infos (Code + n°) peuvent dépasser 79 caractères
!                ======================================================
                 IDBAUX = 79 - LONAUX
                 TITSEM(IDBAUX:IDBAUX) = " "
                 TITSEM(IDBAUX+1:IDBAUX+LONAUX) = TITR132(71+1:71+LONAUX)
              ENDIF
           CASE ("=")
!             ==================
!              Grille constante
!             ==================
              CYCLE BAL_PANN
           END SELECT
!          =========================================================================
!           Cas général : Grille non constante (sinon sautée) : Lecture des valeurs
!          =========================================================================
           SELECT CASE (PANN_EGA)
           CASE DEFAULT
!             ======================
!              Panneau non constant
!             ======================
              DO LIG=1,NLIG
                 IF (IANALY > 0) THEN
!                   ===============
!                    Analyse seule
!                   ===============
                    READ (LEC, *, IOSTAT=IERRAUX)
                    IF (IERRAUX < 0) GO TO 500
                    CYCLE
                 ENDIF
                 LIGAUX = MERGE( LIG , NLIG-LIG+1 , (INVERS == 0) )
                 IND1 = (LIGAUX - 1) * NKOL + INDPAN
                 SELECT CASE (VERSIO)
                 CASE ("8.0")
                    READ (LEC, "(11A12)", IOSTAT=IERRAUX) TABCHAR12(1:10),CHAR12
                 CASE DEFAULT
                    READ (LEC, "(10A7,A10)", IOSTAT=IERRAUX) TABCHAR7(1:10),CHAR10
                 END SELECT
                 IF (IERRAUX > 0) GO TO 450
                 IF (IERRAUX < 0) GO TO 500
                 TABAUX(1:10) = 0.
!                ================================
!                 On cadre à droite par sécurité
!                ================================
                 SELECT CASE (VERSIO)
                 CASE ("8.0")
                    TABCHAR12 = ADJUSTR(TABCHAR12)
                    CHAR12    = ADJUSTR(CHAR12)
                    READ (TABCHAR12(1:10) , "(F12.0)" , IOSTAT=IERRAUX) TABAUX(1:10)
                    IF (IERRAUX > 0) GO TO 450
                    IF (IERRAUX < 0) GO TO 500
                    READ (CHAR12 , "(F12.0)", IOSTAT=IERRAUX) YLIG(LIGAUX)
                    IF (IERRAUX > 0) GO TO 450
                    IF (IERRAUX < 0) GO TO 500
                 CASE DEFAULT
                    TABCHAR7 = ADJUSTR(TABCHAR7)
                    CHAR10   = ADJUSTR(CHAR10)
                    READ (TABCHAR7(1:10) ,"(F7.0)" , IOSTAT=IERRAUX) TABAUX(1:10)
                    IF (IERRAUX > 0) GO TO 450
                    IF (IERRAUX < 0) GO TO 500
                    READ (CHAR10   , "(F10.0)", IOSTAT=IERRAUX) YLIG(LIGAUX)
                    IF (IERRAUX > 0) GO TO 450
                    IF (IERRAUX < 0) GO TO 500
                 END SELECT
                 IF (NTOT > 0) THEN
                    FONC(IND1+1:IND1+NBREEL) = TABAUX(1:NBREEL)
                 ENDIF
              ENDDO
           CASE ("=")
!             ===========================================================================
!              Panneau constant : On ne lit pas les ordonnées
!              (Comme la Grille n'est pas constante elles seront lues au moins une fois)
!             ===========================================================================
              I = 0
              LIG = 999
              READ (LEC, 9004, IOSTAT=IERRAUX) CHAR15
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              READ (CHAR15, *, IOSTAT=IERRAUX) VALEUR
              IF (IERRAUX > 0) GO TO 450
              IF (IANALY == 0) THEN
                 DO LIG=1,NLIG
                    LIGAUX = MERGE(LIG , NLIG-LIG+1 , (INVERS == 0) )
                    IND1 = (LIGAUX - 1) * NKOL + INDPAN
                    IF (NTOT > 0) THEN
                       FONC(IND1+1:IND1+NBREEL) = VALEUR
                    ENDIF
                 ENDDO
              ENDIF
           END SELECT
        ENDDO BAL_PANN
!       =============================
!        Fin de lecture des panneaux
!       =============================
        IF (EGALIT == "=") THEN
!          ================================================================
!           Cas particulier d'une Grille constante : Lecture des ordonnées
!          ================================================================
!          =====================================
!           Séparateur : "Ordonnées des Lignes"
!          =====================================
           READ (LEC, *)
           SELECT CASE (INVERS)
           CASE (0)
              IDEB = 1
              IFIN = NLIG
              IPAS = 1
           CASE DEFAULT
              IDEB = NLIG
              IFIN = 1
              IPAS = -1
           END SELECT
!          =======================
!           Lecture des ordonnées
!          =======================
           SELECT CASE (IANALY)
           CASE (0)
              SELECT CASE (VERSIO)
              CASE ("8.0")
                 READ (LEC, "(10F12.0)", IOSTAT=IERRAUX) YLIG(IDEB:IFIN:IPAS)
              CASE DEFAULT
                 READ (LEC, "(10F7.0)", IOSTAT=IERRAUX)  YLIG(IDEB:IFIN:IPAS)
              END SELECT
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           CASE (1:)
!             ===============
!              Analyse seule
!             ===============
              NBLIG_A_LIRE = (NLIG - 1) / 10 + 1
              DO K=1,NBLIG_A_LIRE
                 READ (LEC, *, IOSTAT=IERRAUX)
              ENDDO
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
           END SELECT
           I = 0
           LIG = 999
           READ (LEC, 9004, IOSTAT=IERRAUX) CHAR15
           IF (IERRAUX > 0) GO TO 450
           IF (IERRAUX < 0) GO TO 500
           READ (CHAR15, *, IOSTAT=IERRAUX) VALEUR
           IF (IERRAUX > 0) GO TO 450
           IF ((NTOT > 0).AND.(IANALY == 0)) FONC(1:NTOT) = VALEUR
        ENDIF
        SELECT CASE (VERSIO)
        CASE ("7.0" , "8.0")
           IEXIS_DX = 1
        CASE DEFAULT
           IEXIS_DX = 0
        END SELECT
        SELECT CASE (IEXIS_DX)
        CASE (1)
!          ======================
!           Lecture des DX et DY
!          ======================
           IF (LIRE_DXDY > 0) THEN
              READ (LEC, "(T31,F11.0)", IOSTAT=IERRAUX) X0_PRECIS
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              READ (LEC, *, IOSTAT=IERRAUX) DXLU(1:NKOL)
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              READ (LEC, "(T31,F11.0)", IOSTAT=IERRAUX) Y0_PRECIS
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
              SELECT CASE (INVERS)
              CASE (:0)
                 READ (LEC, *, IOSTAT=IERRAUX) DYLU(1:NLIG)
              CASE DEFAULT
!                =================
!                 INVERS = 1 ou 2
!                =================
                 READ (LEC, *, IOSTAT=IERRAUX) DYLU(NLIG:1:-1)
              END SELECT
              IF (IERRAUX > 0) GO TO 450
              IF (IERRAUX < 0) GO TO 500
!             ===================================================
!              Léger risque que non identique au précédent ... !
!             ===================================================
              X0 = X0_PRECIS
              Y0 = Y0_PRECIS
              LU_DXDY = 1
              IF ((ALL( DYLU(1:NLIG) > 0.)).AND. &
                  (ALL( DXLU(1:NKOL) > 0.))) THEN
!                ================================================================
!                Recalcul des XCOL et YLIG à partir des DXLU, DYLU (plus précis)
!                ================================================================
                 CALL DXDY_XCOLYLIG( DXLU, DYLU, XCOL, YLIG, X0, Y0, NLIG, NKOL, INVERS )
              ENDIF
!             ==============================================
!              Lecture du separateur de fin : "! End Coord"
!             ==============================================
              READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
           ELSE
!             =============================
!              Saute les lignes des DX, DY
!             =============================
              SAUTE_DX: DO WHILE (.TRUE.)
                 READ (LEC, "(A)", IOSTAT=IERRAUX) TITR132
                 IF (IERRAUX > 0) EXIT SAUTE_DX
                 IF (IERRAUX < 0) EXIT SAUTE_DX
                 DO K=1,20
                    IF ((TITR132(K:K+11) == "** End Semis").OR. &
                        (TITR132(K:K+11) == "** end semis").OR. &
                        (TITR132(K:K+11) == "** END SEMIS")) THEN
                       EXIT SAUTE_DX
                    ENDIF
                 ENDDO
              ENDDO SAUTE_DX
              LU_DXDY = 0
           ENDIF
        CASE (0)
           LU_DXDY = 0
        END SELECT
        GO TO 999
!       =========
!        Erreurs
!       =========
  450   NUMERR = I
        IERLEC = 1
        GO TO 999
  500   NUMERR = I
        IERLEC = 2
        GO TO 999
  520   IERLEC = -1
    999 CONTINUE
   9004 FORMAT (18X,A15)
   9005 FORMAT (T9,A1,T17,I3,T27,A3,T31,A,T35,I4,T50,I4,T63,F7.0,T74,F7.0)
   9011 FORMAT (T9,A1,T17,I3,T27,A3,T31,A,T35,I4,T51,I4,T64,F12.0,T81,F12.0)
   9006 FORMAT (" ***********************************************************" &
               /" * Sous-dimensionnement dans la lecture de Grille",T60,"*" &
               /" * Nb Lignes  = ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" * Nb Colonnes= ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" * Nb Points  = ",I0," (Maxi prévu ou précéd: ",I0,")" &
               /" *              Fin d'exécution probable",T60,"*" &
               /" ***********************************************************")
   9007 FORMAT (" *** Fin normale de la lecture de cette Grille ***")
   9008 FORMAT (/" ** Erreur de lecture ligne ",I0," panneau ",I0," **")
   9009 FORMAT (" ** Erreur de lecture des caractéristiques de la Grille **" &
               /"    (",I0," Pann., ",I0," Lignes, ",I0," Colonnes)")
   9010 FORMAT (" ***********************************************************" &
               /" * Incohérence dans la 'grille' au panneau : ",I0,T60,"*" &
               /" * Nb Lignes  = ",I0," (Panneau précéd : ",I0,")",T60,"*" &
               /" * Nb Colonnes= ",I0," (panneau précéd : ",I0,")",T60,"*" &
               /" *            Stop",T60,"*" &
               /" ***********************************************************")
        END SUBROUTINE LECSEM_FORMAT_FIXE
        SUBROUTINE LESEMI_Lit_Info_Complem(TITR132, TYP_DON, TYP_DON3, DATE &
                   , N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
                   , IERR)
!       ===================================
!        Lecture des infos complémentaires
!       ===================================
        IMPLICIT NONE
        CHARACTER (LEN=*), INTENT(IN) :: TITR132
        REAL    , INTENT(IN OUT):: DATE
        CHARACTER (LEN=*), INTENT(IN OUT) :: TYP_DON
        CHARACTER (LEN=*), INTENT(IN OUT) :: TYP_DON3
        INTEGER, INTENT(IN OUT) :: IERR
        INTEGER, INTENT(IN OUT) :: N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX
!       ========
!        Locaux
!       ========
        INTEGER :: IPOSIT_1, IPOSIT_2, IERR2
!       =======
!        Début
!       =======
         IERR = 0
         IPOSIT_1 = 0
         IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "<")
         IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
         IF (IPOSIT_2 > 0) THEN
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ">")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
         ELSE
            IERR = 1
         ENDIF
         IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
            TYP_DON = TITR132(IPOSIT_1+1:IPOSIT_2-1)
         ELSE
            IERR = 1
         ENDIF
         IF (IPOSIT_2 > 0) THEN
            IPOSIT_1 = INDEX(TITR132(IPOSIT_2+1:) , "/")
            IF (IPOSIT_1 > 0) IPOSIT_1 = IPOSIT_1 + IPOSIT_2
            IF (IPOSIT_1 > 0) THEN
               IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "/")
               IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            ELSE
               IPOSIT_2 = 0
               IERR = 1
            ENDIF
            IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
               TYP_DON3 = TITR132(IPOSIT_1+1:IPOSIT_2-1)
            ELSE
               IERR = 1
            ENDIF
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           =============
!            "/N_ELECH;"
!           =============
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ";")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
         ENDIF
         IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
            READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) N_ELEMCH
            IF (IERR2 /= 0) IERR = IERR2
         ELSE
            IERR = 1
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ===================
!            "; Step=      0;"
!           ===================
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "=")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            IF (IPOSIT_2 > 0) THEN
               IPOSIT_1 = IPOSIT_2
               IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ";")
               IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            ELSE
               IERR = 1
            ENDIF
            IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
               READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) ISTEP
               IF (IERR2 /= 0) IERR = IERR2
            ELSE
               IERR = 1
            ENDIF
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ===============
!            "Lay=1234/"
!           ===============
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "=")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            IF (IPOSIT_2 > 0) THEN
               IPOSIT_1 = IPOSIT_2
               IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "/")
               IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            ELSE
               IERR = 1
            ENDIF
            IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
               READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) N_COUCH
               IF (IERR2 /= 0) IERR = IERR2
            ELSE
               IERR = 1
            ENDIF
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ==========
!            "/   1;"
!           ==========
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ";")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
         ENDIF
         IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
            READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) NCOUC_MX
            IF (IERR2 /= 0) IERR = IERR2
         ELSE
            IERR = 1
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ==============
!            "Nest= 0/"
!           ==============
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "=")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            IF (IPOSIT_2 > 0) THEN
               IPOSIT_1 = IPOSIT_2
               IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "/")
               IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            ELSE
               IERR = 1
            ENDIF
            IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
               READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) NU_ZOO
               IF (IERR2 /= 0) IERR = IERR2
            ELSE
               IERR = 1
            ENDIF
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ==========
!            "/ 0;"
!           ==========
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ";")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
         ENDIF
         IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
            READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) NU_ZOOMX
            IF (IERR2 /= 0) IERR = IERR2
         ELSE
            IERR = 1
         ENDIF
         IF (IPOSIT_2 > 0) THEN
!           ===================================================
!            "T= 0.0000E+00;"
!            N.B. Pas forcément de ";" (dans fichiers anciens)
!           ===================================================
            IPOSIT_1 = IPOSIT_2
            IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , "=")
            IF (IPOSIT_2 > 0) IPOSIT_2 = IPOSIT_2 + IPOSIT_1
            IF (IPOSIT_2 > 0) THEN
               IPOSIT_1 = IPOSIT_2
               IPOSIT_2 = INDEX(TITR132(IPOSIT_1+1:) , ";")
               IF (IPOSIT_2 > 0) THEN
                  IPOSIT_2 = IPOSIT_2 + IPOSIT_1
               ELSE
!                 ===================================================
!                  N.B. Pas forcément de ";" (dans fichiers anciens)
!                  N.B. On rajoute 1 car comme si le ";" était placé
!                       juste après la fin de ligne
!                 ===================================================
                  IPOSIT_2 = LEN_TRIM(TITR132) + 1
               ENDIF
            ELSE
               IERR = 1
            ENDIF
            IF ((IPOSIT_1 > 0).AND.(IPOSIT_2 > IPOSIT_1+1)) THEN
               READ (TITR132(IPOSIT_1+1:IPOSIT_2-1), *, IOSTAT=IERR2) DATE
               IF (IERR2 /= 0) IERR = IERR2
            ELSE
               IERR = 1
            ENDIF
         ENDIF
        END SUBROUTINE LESEMI_Lit_Info_Complem
        SUBROUTINE LESEM_GRD(FONC, X0, Y0, XCOL, YLIG &
                           , NLIG, NKOL, NTOT, LEC, INVERS, FMANQ, DXLU, DYLU &
                           , IERLEC, NUMERR &
                           , IANALY)
!       ============================================
!        Lecture d'une Grille GRD ASCII de "Surfer"
!       ============================================
!       ========================================================================
!        NTOT      = Nombre maxi de places dans le tableau FONC()
!                    Si NTOT = 0 on ne lit pas les points mais seulement
!                    les coordonnées [il n'y a rien dans FONC()]
!        NKOL      = Nombre maxi de places dans les tableaux XCOL(), DXLU()
!        NLIG      = Nombre maxi de places dans les tableaux YLIG(), DYLU()
!        IERLEC =  0 Si normal
!        IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!        IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!        IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!        IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!       ========================================================================
        IMPLICIT NONE
        REAL   , INTENT(IN) :: FMANQ
        INTEGER, INTENT(IN) :: INVERS, LEC, IANALY
        INTEGER, INTENT(IN OUT) :: NTOT
        INTEGER, INTENT(IN OUT) :: NLIG, NKOL
        REAL   , INTENT(OUT), DIMENSION(*) :: FONC
        REAL   , INTENT(OUT), DIMENSION(*) :: DXLU, XCOL
        REAL   , INTENT(OUT), DIMENSION(*) :: DYLU, YLIG
        REAL   , INTENT(OUT) :: X0, Y0
        INTEGER, INTENT(OUT) :: IERLEC, NUMERR
!       ========
!        Locaux
!       ========
        REAL    :: XMIN, XMAX, YMIN, YMAX, CMIN_FICTIF, CMAX_FICTIF, FMANQ_SURFER &
                 , DX_CONST, DY_CONST
        INTEGER :: LIG, INDLIG, IERRAUX, NEED, NKOLMA, NLIGMA
!       =======
!        Début
!       =======
        FMANQ_SURFER = 0.9e38
        IERLEC = 0
        NUMERR = 0
        NKOLMA = NKOL
        NLIGMA = NLIG
        DXLU(1) = 0.
        XCOL(1) = 0.
        DYLU(1) = 0.
        YLIG(1) = 0.
        READ (LEC, *, IOSTAT=IERRAUX) NKOL, NLIG, XMIN, XMAX, YMIN, YMAX &
                                    , CMIN_FICTIF, CMAX_FICTIF
        IF (IERRAUX /= 0) THEN
           IERLEC = -1
           GO TO 999
        ENDIF
        IF ((NLIG <= 0).OR.(NKOL <= 0)) THEN
           IERLEC = -1
           GO TO 999
        ENDIF
        NEED = NLIG * NKOL
!       ====================================================================================
!        Si Analyse Seule => Fini [Pas lecture de FONC() ni XCOL(), YLIG(), DXLU(), DYLU()]
!       ====================================================================================
        IF (IANALY >= 1) GO TO 999
        IF ((NLIG > NLIGMA).OR.(NKOL > NKOLMA).OR. &
            ((NEED > NTOT).AND.(NTOT /= 0)) ) THEN
           NKOL = NKOLMA
           NLIG = NLIGMA
           IERLEC = 3
           GO TO 999
        ENDIF
!       ========================================================================
!        * Il faut lire la Première ligne en Bas
!        * Pour Surfer (Wire) Valeur Manquante = HUGE(REAL) en Simple Précision
!          C-à-d Valeur Manquante = 1.70141(17)e38
!       ========================================================================
        SELECT CASE (NTOT)
        CASE (1:)
!          ======================================================
!           Voir : Selon INVERS : Pas toujours besoin d'inverser
!          ======================================================
           DO LIG=NLIG,1,-1
              INDLIG = (LIG-1) * NKOL
              READ (LEC, *, IOSTAT=IERRAUX) FONC(INDLIG+1:INDLIG+NKOL)
              SELECT CASE (IERRAUX)
              CASE (:-1)
                 IERLEC = 2
                 NUMERR = INDLIG + 1
              CASE (1:)
                 IERLEC = 1
                 NUMERR = INDLIG + 1
              END SELECT
              IF (IERRAUX /= 0) GO TO 999
           ENDDO
           WHERE (FONC(1:NLIG*NKOL) >= FMANQ_SURFER) &
                  FONC(1:NLIG*NKOL) = FMANQ
           NTOT = NEED
        CASE (:0)
!          ====================================================
!           On saute les lignes (FONC() n'est pas dimensionné)
!           => Uniquement XCOL() et YLIG()
!          ====================================================
           DO LIG=1,NLIG
              READ (LEC, *, IOSTAT=IERRAUX)
           ENDDO
        END SELECT
        DX_CONST = (XMAX - XMIN) / MAX( (NKOL - 1.) , 1.)
        IF (DX_CONST <= 0.) DX_CONST = 1.
        DY_CONST = (YMAX - YMIN) / MAX( (NLIG - 1.) , 1.)
        IF (DY_CONST <= 0.) DY_CONST = 1.
        X0 = XMIN - 0.5 * DX_CONST
        Y0 = YMIN - 0.5 * DY_CONST
        DXLU(1:NKOL) = DX_CONST
        DYLU(1:NLIG) = DY_CONST
!       =====================================================
!        Calcul des XCOL et YLIG à partir des DXLU(), DYLU()
!       =====================================================
        CALL DXDY_XCOLYLIG( DXLU, DYLU, XCOL, YLIG, X0, Y0, NLIG, NKOL, INVERS )
    999 CONTINUE
        END SUBROUTINE LESEM_GRD
        SUBROUTINE LESEM_ARCVIEW_ASC(FONC, X0, Y0, XCOL, YLIG &
                           , NLIG, NKOL, NTOT, LEC, INVERS, FMANQ, DXLU, DYLU &
                           , IERLEC, NUMERR &
                           , IANALY, TITAUX, ITYP_ARCVIEW)
!       ===========================================
!        Lecture d'une grille ASC ASCII de Arcview
!       ===========================================
!       ========================================================================
!        TITAUX    = Première ligne
!        NTOT      = Nombre maxi de places dans le tableau FONC()
!                    Si NTOT = 0 on ne lit pas les points mais seulement
!                    les coordonnées [Il n'y a rien dans FONC()]
!        NKOL      = Nombre maxi de places dans le tableau XCOL(), DXLU()
!        NLIG      = Nombre maxi de places dans le tableau YLIG(), DYLU()
!        IERLEC =  0 Si normal
!        IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!        IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!        IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!        IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!       ========================================================================
        IMPLICIT NONE
        REAL   , INTENT(IN)  :: FMANQ
        INTEGER, INTENT(IN)  :: INVERS, LEC, IANALY
        INTEGER, INTENT(OUT) :: ITYP_ARCVIEW
        INTEGER, INTENT(IN OUT) :: NTOT
        INTEGER, INTENT(IN OUT) :: NLIG, NKOL
        CHARACTER (LEN=*), INTENT(IN OUT) :: TITAUX
        REAL   , INTENT(OUT), DIMENSION(*) :: FONC
        REAL   , INTENT(OUT), DIMENSION(*) :: DXLU, XCOL
        REAL   , INTENT(OUT), DIMENSION(*) :: DYLU, YLIG
        REAL   , INTENT(OUT) :: X0, Y0
        INTEGER, INTENT(OUT) :: IERLEC, NUMERR
!       ==============================================================================
!        Attention : Pas de déclaration : CHARACTER (LEN=500)  :: TRANSFO_EN_MAJUSC_2
!        Puisque déclaré dans le CONTAINS => Sinon serait cherché comme un EXTERNAL !
!       ==============================================================================
!       ========
!        Locaux
!       ========
        CHARACTER (LEN=15) :: LAB15, LAB_ELSE_15
        REAL    :: VALEUR, FMANQ_FICH &
                 , DX_CONST, DY_CONST
        INTEGER :: LIG, INDLIG, IERRAUX, NEED, NKOLMA, NLIGMA, K, IDEB, LIG_RANGE &
                 , LENGTH, I_X0_CEN, I_Y0_CEN
!       =======
!        Début
!       =======
        IERLEC = 0
        NUMERR = 0
        ITYP_ARCVIEW = 1
        NKOLMA = NKOL
        NLIGMA = NLIG
        DXLU(1) = 0.
        XCOL(1) = 0.
        DYLU(1) = 0.
        YLIG(1) = 0.
!       ===============================
!        Lecture du nombre de Colonnes
!       ===============================
        TITAUX = TRANSFO_EN_MAJUSC_2(TITAUX)
        IDEB = INDEX(TITAUX , "NCOLS")
        IF (IDEB <= 0) THEN
           ITYP_ARCVIEW = 0
           GO TO 999
        ELSE
           READ (TITAUX(IDEB+6:), *, IOSTAT=IERRAUX) NKOL
           IF (IERRAUX /= 0) NKOL = 0
           IF (NKOL <= 0) THEN
              ITYP_ARCVIEW = 0
              NKOL = NKOLMA
              GO TO 999
           ENDIF
        ENDIF
!       =============================
!        Lecture du nombre de Lignes
!       =============================
        READ (LEC, "(A)", IOSTAT=IERRAUX) TITAUX
        IF (IERRAUX /= 0) THEN
           ITYP_ARCVIEW = 0
           GO TO 999
        ENDIF
        TITAUX = TRANSFO_EN_MAJUSC_2(TITAUX)
        IDEB = INDEX(TITAUX , "NROWS")
        IF (IDEB <= 0) THEN
           ITYP_ARCVIEW = 0
           GO TO 999
        ELSE
           READ (TITAUX(IDEB+6:), *, IOSTAT=IERRAUX) NLIG
           IF (IERRAUX /= 0) NLIG = 0
           IF (NLIG <= 0) THEN
              ITYP_ARCVIEW = 0
              NLIG = NLIGMA
!             ================================================
!              On recule => dernière chance => Grille normale
!             ================================================
              BACKSPACE (LEC)
              GO TO 999
           ENDIF
        ENDIF
!       ==================================================================
!        Ici on a lu NKOL et NLIG => Si erreur => Plus de retour possible
!       ==================================================================
!       ====================================================================
!        Lecture de "xllcorner" , "yllcorner" , "cellsize" , "NODATA_value"
!        ou bien de "xllcenter" , "yllcenter" , "cellsize" , "NODATA_value"
!       ====================================================================
        I_X0_CEN = 0
        I_Y0_CEN = 0
        DO K=1,4
           SELECT CASE (K)
           CASE (1)
              LAB15 = "XLLCORNER"
              LAB_ELSE_15 = "XLLCENTER"
           CASE (2)
              LAB15 = "YLLCORNER"
              LAB_ELSE_15 = "YLLCENTER"
           CASE (3)
              LAB15 = "CELLSIZE"
              LAB_ELSE_15 = LAB15
           CASE (4)
              LAB15 = "NODATA_VALUE"
              LAB_ELSE_15 = LAB15
           END SELECT
           READ (LEC, "(A)", IOSTAT=IERRAUX) TITAUX
           IF (IERRAUX /= 0) THEN
              IERLEC = -1
              GO TO 999
           ENDIF
           LENGTH = LEN_TRIM(LAB15)
           TITAUX = TRANSFO_EN_MAJUSC_2(TITAUX)
           IDEB = INDEX(TITAUX , TRIM(LAB15))
           IF (IDEB <= 0) THEN
              IDEB = INDEX(TITAUX , TRIM(LAB_ELSE_15))
              LENGTH = LEN_TRIM(LAB_ELSE_15)
              SELECT CASE (K)
              CASE (1)
                 I_X0_CEN = 1
              CASE (2)
                 I_Y0_CEN = 1
              END SELECT
           ENDIF
           IF (IDEB <= 0) THEN
              IERLEC = -1
              GO TO 999
           ELSE
              READ (TITAUX(IDEB+LENGTH+1:), *, IOSTAT=IERRAUX) VALEUR
           ENDIF
           IF (IERRAUX /= 0) THEN
              IERLEC = -1
              GO TO 999
           ENDIF
           SELECT CASE (K)
           CASE (1)
              X0 = VALEUR
           CASE (2)
              Y0 = VALEUR
           CASE (3)
              DX_CONST = VALEUR
              DY_CONST = VALEUR
           CASE (4)
              FMANQ_FICH = VALEUR
           END SELECT
        ENDDO
        IF (I_X0_CEN == 1) X0 = X0 - 0.5 * DX_CONST
        IF (I_Y0_CEN == 1) Y0 = Y0 - 0.5 * DY_CONST
        NEED = NLIG * NKOL
!       ====================================================================================
!        Si Analyse Seule => Fini [Pas lecture de FONC() ni XCOL(), YLIG(), DXLU(), DYLU()]
!       ====================================================================================
        IF (IANALY >= 1) GO TO 999
        IF ((NLIG > NLIGMA).OR.(NKOL > NKOLMA).OR. &
            ((NEED > NTOT).AND.(NTOT /= 0)) ) THEN
           NKOL = NKOLMA
           NLIG = NLIGMA
           IERLEC = 3
           GO TO 999
        ENDIF
        SELECT CASE (NTOT)
        CASE (1:)
!          =====================
!           Lecture des données
!          =====================
           DO LIG=1,NLIG
              SELECT CASE (INVERS)
              CASE (0)
!                ============================================
!                 Première Ligne en premier => Sans problème
!                ============================================
                 LIG_RANGE = LIG
              CASE (1:)
!                ======================================
!                 Première Ligne lue rangée en dernier
!                ======================================
                 LIG_RANGE = NLIG - LIG + 1
              END SELECT
              INDLIG = (LIG_RANGE - 1) * NKOL
              READ (LEC, *, IOSTAT=IERRAUX) FONC(INDLIG+1:INDLIG+NKOL)
              SELECT CASE (IERRAUX)
              CASE (:-1)
                 IERLEC = 2
                 NUMERR = INDLIG + 1
              CASE (1:)
                 IERLEC = 1
                 NUMERR = INDLIG + 1
              END SELECT
              IF (IERRAUX /= 0) GO TO 999
           ENDDO
           WHERE (FONC(1:NLIG*NKOL) == FMANQ_FICH) &
                  FONC(1:NLIG*NKOL) = FMANQ
           NTOT = NEED
        CASE (:0)
!          ====================================================
!           On saute les lignes [FONC() n'est pas dimensionné]
!           => Uniquement XCOL() et YLIG()
!          ====================================================
           DO LIG=1,NLIG
              READ (LEC, *, IOSTAT=IERRAUX)
           ENDDO
        END SELECT
        DXLU(1:NKOL) = DX_CONST
        DYLU(1:NLIG) = DY_CONST
!       =========================================================
!        Calcul des XCOL() et YLIG() à partir des DXLU(), DYLU()
!       =========================================================
        CALL DXDY_XCOLYLIG( DXLU, DYLU, XCOL, YLIG, X0, Y0, NLIG, NKOL, INVERS )
    999 CONTINUE
        END SUBROUTINE LESEM_ARCVIEW_ASC
        SUBROUTINE LESEM_LIBRE(FONC, NTOT, LEC, INVERS &
                             , IERLEC, NUMERR, IANALY)
!       ======================================
!        Lecture d'une Grille en Format Libre
!        tout à la suite
!       ======================================
!       ========================================================================
!        NTOT      = Nombre maxi de places dans le tableau FONC()
!                    Si NTOT = 0 on ne lit pas les points mais seulement
!                    les coordonnées [il n'y a rien dans FONC()]
!        INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
!               : 1 = Inversion la première ligne lue est rangée en dernier
!        IERLEC =  0 Si normal
!        IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!        IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!       ========================================================================
        IMPLICIT NONE
        INTEGER, INTENT(IN) :: INVERS, LEC, IANALY
        INTEGER, INTENT(IN) :: NTOT
        REAL   , INTENT(OUT), DIMENSION(*) :: FONC
        INTEGER, INTENT(OUT) :: IERLEC, NUMERR
!       ========
!        Locaux
!       ========
        INTEGER :: IERRAUX
!       =======
!        Début
!       =======
        IERLEC = 0
        NUMERR = 0
!       ====================================================================================
!        Si Analyse Seule => Fini [Pas lecture de FONC() ni XCOL(), YLIG(), DXLU(), DYLU()]
!       ====================================================================================
        IF (IANALY >= 1) GO TO 999
        SELECT CASE (NTOT)
        CASE (1:)
!          ======================================================
!           Voir : Selon INVERS : Pas toujours besoin d'inverser
!          ======================================================
           READ (LEC, *, IOSTAT=IERRAUX) (FONC(I), I=1,NTOT)
           SELECT CASE (IERRAUX)
           CASE (:-1)
              IERLEC = 2
              NUMERR = 1
           CASE (1:)
              IERLEC = 1
              NUMERR = 1
           END SELECT
           IF (IERRAUX /= 0) GO TO 999
           IF (INVERS == 1) THEN
!             =================================
!              Voir ... Operasem ou autres ...
!             =================================
           ENDIF
        END SELECT
    999 CONTINUE
        END SUBROUTINE LESEM_LIBRE
        CHARACTER (LEN=500) FUNCTION TRANSFO_EN_MAJUSC_2(STRING)
!       ======================================================================
!       *********************
!       *TRANSFO_EN_MAJUSC_2*              BRGM     B.P. 36009
!       *********************              45060 Orléans Cédex
!       Auteur(s):THIERY D.
!       Date: 22/12/2019
!       ======================================================================
!        Passage en Majuscule de la Chaine STRING
!        N.B. 500 caractères maxi
!        N.B. Utilisation : Ne Pas déclarer dans une INTERFACE
!        Puisque dans le CONTAINS => Sinon serait cherché comme un EXTERNAL !
!        N.B. Utilisation :
!             CHAIN_MAJUSC = TRANSFO_EN_MAJUSC_2(CHAINE)
!         ou bien :
!             WRITE (*, "(A)") TRIM( TRANSFO_EN_MAJUSC_2(CHAINE) )
!       ======================================================================
        IMPLICIT NONE
        CHARACTER (LEN=*), INTENT(IN) :: STRING
!       ========
!        Locaux
!       ========
        INTEGER :: KK, J
!       =======
!        Début
!       =======
        TRANSFO_EN_MAJUSC_2 = STRING
        IF (LEN_TRIM(STRING) <= 0) THEN
           TRANSFO_EN_MAJUSC_2 = " "
        ELSE
           DO KK=1,MIN(LEN_TRIM(STRING) , 500)
              J = IACHAR( STRING(KK:KK) )
              SELECT CASE (J)
              CASE (97:122)
!                ==========================
!                 Minuscules => Majuscules
!                ==========================
                 J = J - 32
                 TRANSFO_EN_MAJUSC_2(KK:KK) = ACHAR(J)
              END SELECT
           ENDDO
        ENDIF
        END FUNCTION TRANSFO_EN_MAJUSC_2
      END SUBROUTINE LECSEM_3
      SUBROUTINE DIMSEM(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC)
!============================================================================
!   **********
!   *DIMSEM  *                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!============================================================================
!        Grille de points : Analyse des dimensions
!        Version 2.1
!============================================================================
!     LEC      = Unité de Lecture
!     IOUCON   = Unité Logique d'écriture sur la console    si > 0
!                Seulement écriture des erreurs sur console si = 0
!                Pas d'écriture                             si < 0
!     N.B.        Si NTOT = 0 On ne lit pas les points mais seulement
!                 les coordonnées (Il n'y a rien dans le tableau FONC)
!     En Retour :
!     TITSEM = Dernier titre lu pour la Grille (len=132)
!     NLIG   = Nombre de Lignes
!     NKOL   = Nombre de Colonnes
!     IERLEC =  0 Si normal
!     IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!     IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!     IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!     IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!============================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: IOUCON, LEC
      INTEGER, INTENT(OUT) :: NLIG, NKOL, IERLEC
      CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM
!     ============================================
!      Tableaux automatiques et variables locales
!     ============================================
      REAL   , DIMENSION(2) :: FONC, XCOL, YLIG
      REAL   , DIMENSION(9999) :: DXLU, DYLU
      CHARACTER (LEN=13) :: TYP_DON
      CHARACTER (LEN=7)  :: TYP_DON3
      CHARACTER (LEN=80) :: LIBCHIM
      INTEGER :: LIRE_DXDY, LU_DXDY, LU_XY, IANALY, INVERS, NUMERR, NTOT &
               , N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX
      REAL    :: X0, Y0, DATE
!     =======
!      Début
!     =======
      NLIG = 0
      NKOL = 0
      N_COUCH = 0
      IANALY = 1
      LIRE_DXDY = 0
!     ====================================
!      Appel avec 1 + 9 arguments en plus
!     ====================================
      CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
      END SUBROUTINE DIMSEM
      SUBROUTINE ANASEM_2(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM)
!======================================================================================
!   **********
!   *ANASEM_2*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!======================================================================================
!        Grille de points : Analyse des Dimensions et Caractéristiques
!        Version 2.1
!======================================================================================
!     LEC      = Unité de Lecture
!     IOUCON   = Unité Logique d'écriture sur la console    si > 0
!                Seulement écriture des erreurs sur console si = 0
!                Pas d'écriture                             si < 0
!     N.B.        Si NTOT = 0 On ne lit pas les points, mais seulement les coordonnées
!                 (Dans ce cas, il n'y a rien dans le tableau FONC)
!     En Retour :
!     TITSEM = Dernier titre lu pour la Grille (len=132)
!     NLIG   = Nombre de Lignes
!     NKOL   = Nombre de Colonnes
!     IERLEC =  0 Si normal
!     IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!     IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!     IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!     IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!======================================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: LEC, IOUCON
      INTEGER, INTENT(OUT) :: NLIG, NKOL, IERLEC
      INTEGER :: N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX
      REAL    :: DATE
      CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM
      CHARACTER (LEN=*)  :: LIBCHIM
      CHARACTER (LEN=13) :: TYP_DON
      CHARACTER (LEN=7)  :: TYP_DON3
!     ========
!      Locaux
!     ========
      REAL   , DIMENSION(2) :: FONC, XCOL, YLIG
      REAL   , DIMENSION(9999) :: DXLU, DYLU
      REAL    :: X0, Y0
      INTEGER :: LIRE_DXDY, LU_DXDY, LU_XY, IANALY, NTOT, INVERS, NUMERR
!     =======
!      Début
!     =======
      IANALY = 1
      LIRE_DXDY = 0
!     ====================================
!      Appel avec 1 + 9 arguments en plus
!     ====================================
      CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
      END SUBROUTINE ANASEM_2
      SUBROUTINE SAUTE_SEM(NB_SAUTE, LEC)
!=======================================================================
!   ***********
!   *SAUTE_SEM*                        BRGM     B.P. 36009
!   ***********                        45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!        Saut de NB_SAUTE Grilles à partir du début du Fichier
!        Pour se placer juste avant la grille n°NB_SAUTE + 1
!=======================================================================
!      En Entrée :
!       NB_SAUTE = Nombre de Grilles à Sauter
!       LEC      = Unité logique sur laquelle a été ouvert le fichier
!      En Retour :
!       La Grille n°NB_SAUTE + 1 est prête à être lu
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NB_SAUTE, LEC
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=132) :: TITSEM
      INTEGER :: I, IOUCON, NLIG, NKOL, IERLEC
!     =======
!      Début
!     =======
      TITSEM = "<Unknown>"
      REWIND (LEC)
      IOUCON = 0
      DO I=1,NB_SAUTE
         CALL DIMSEM(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC)
         IF (IERLEC /= 0) EXIT
      ENDDO
      END SUBROUTINE SAUTE_SEM
      SUBROUTINE SAUTE_SEMIS_FROM(NB_SAUTE , LEC)
!=======================================================================
!   ******************
!   *SAUTE_SEMIS_FROM*                 BRGM     B.P. 36009
!   ******************                 45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!        Saut de NB_SAUTE Grilles après la Grille courante
!=======================================================================
!      En Entrée :
!       NB_SAUTE = Nombre de Grilles à sauter après la Grille courante
!       LEC      = Unité logique sur laquelle a été ouvert le fichier
!      En Retour :
!       NB_SAUTE Grilles ont été sautées.
!       Donc si on avait lu la Grille n°N :
!       => N + NB_SAUTE Grilles ont été lues
!       => Prêt à lire la Grille n°N + NB_SAUTE + 1
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NB_SAUTE, LEC
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=132) :: TITSEM
      INTEGER :: I, IOUCON, NLIG, NKOL, IERLEC
!     =======
!      Début
!     =======
!     ======================
!      N.B. PAS de Rewind !
!     ======================
      TITSEM = "<Unknown>"
      IOUCON = 0
      DO I=1,NB_SAUTE
         CALL DIMSEM(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC)
         IF (IERLEC /= 0) EXIT
      ENDDO
      END SUBROUTINE SAUTE_SEMIS_FROM
      SUBROUTINE ANA_MULTI_SEM_2(NSEM_MAX, LEC &
        , NB_PAQU, NB_SAUTE, TYP_DON_T, TYP_DON3_T, DATE_T, N_ELEMCH_T &
        , ISTEP_T, NCOUC_MX_T, NU_ZOO_T, NU_ZOOMX_T, LIBCHIM_T)
!==================================================================================
!   *****************
!   *ANA_MULTI_SEM_2*                  BRGM     B.P. 36009
!   *****************                  45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!==================================================================================
!        ANA(lyse) M(ulti) SEM(is)
!        Analyse des Grilles d'un ensemble de Grilles
!==================================================================================
!      En Entrée :
!       Nombre maxi de Grilles à lire NSEM_MAX , LEC
!       NSEM_MAX = Nombre maxi d'ensembles de Grilles à lire (par exemple 2000)
!                  Un ensemble de Grilles comprend 1 Grille pour chaque Couche
!       LEC      = Unité logique sur laquelle a été ouvert le fichier à analyser
!      En Retour :
!       NB_PAQU  = Nombre d'Ensembles de Grilles lues
!                  Un Ensemble de Grilles comprend 1 Grille pour chaque Couche
!        Informations pour chaque Ensemble de Grilles lues :
!        NB_SAUTE(I)   = Nombre de Grilles à "sauter" pour atteindre l'ensemble n°I
!                            INTEGER , DIMENSION (NSEM_MAX)
!        TYP_DON_T (I) = Code de 13 caractères de l'ensemble n°I
!        TYP_DON3_T(I) = Code complémentaire de 3 caractères (existant parfois)
!        ISTEP_T   (I) = Numéro du Pas de Temps de l'ensemble n°I
!        DATE_T    (I) = Date de l'ensemble n°I
!        N_ELEMCH_T(I) = Numéro de l'Élément Chimique (0 par défaut)
!        NCOUC_MX_T(I) = Nombre de Couches à lire dans l'ensemble n°I
!        NU_ZOO_T  (I) = Numéro du Gigone de l'Ensemble n°I (Défaut=0)
!        NU_ZOOMX_T(I) = Nombre Total de Gigognes (Défaut=0)
!         Toutes ces infos sont de : DIMENSION (NSEM_MAX)
!         Toutes ces infos sont des INTEGER :
!         Sauf : DATE_T        : REAL (SINGLE) , DIMENSION (NSEM_MAX)
!                TYP_DON_T(I)  : CHARACTER (LEN=13)
!                TYP_DON3_T(I) : CHARACTER (LEN=7)
!        LIBCHIM_T(I) = Libellé Complémentaire de l'ensemble n°I [Character 80]
!                     = Nom de l'Élément Chimique par exemple
!==================================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NSEM_MAX, LEC
      INTEGER, INTENT(OUT) :: NB_PAQU
      CHARACTER (LEN=*), DIMENSION(NSEM_MAX) :: TYP_DON_T
      CHARACTER (LEN=7), DIMENSION(NSEM_MAX) :: TYP_DON3_T
      CHARACTER (LEN=*), DIMENSION(NSEM_MAX) :: LIBCHIM_T
      REAL   , DIMENSION(NSEM_MAX) :: DATE_T
      INTEGER, DIMENSION(NSEM_MAX) :: N_ELEMCH_T, ISTEP_T &
                                    , NCOUC_MX_T, NU_ZOO_T, NU_ZOOMX_T &
                                    , NB_SAUTE
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=132) :: TITSEM
      CHARACTER (LEN=13)  :: TYP_DON
      CHARACTER (LEN=7)   :: TYP_DON3
      CHARACTER (LEN=80)  :: LIBCHIM
      REAL    :: DATE
      INTEGER :: IOUCON, IERLEC, KONT, KONT_SEM, NCO, IZO, NLIG, NKOL, N_COUCH &
               , N_ELEMCH, ISTEP, NCOUC_MX, NU_ZOO, NU_ZOOMX
!     =======
!      Début
!     =======
      IOUCON = 0
      IERLEC = 0
      NLIG = 0
      NKOL = 0
      N_COUCH = 0
      KONT = 0
      KONT_SEM = 0
      TITSEM = "<Unknown>"
      DO WHILE (KONT < NSEM_MAX)
         CALL ANASEM_2(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC &
           , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
           , DATE, LIBCHIM)
         IF (IERLEC /= 0) EXIT
         KONT = KONT + 1
         NB_SAUTE  (KONT) = KONT_SEM
         TYP_DON_T (KONT) = TYP_DON
         TYP_DON3_T(KONT) = TYP_DON3
         DATE_T    (KONT) = DATE
         N_ELEMCH_T(KONT) = N_ELEMCH
         ISTEP_T   (KONT) = ISTEP
         NCOUC_MX_T(KONT) = NCOUC_MX
         NU_ZOO_T  (KONT) = NU_ZOO
         NU_ZOOMX_T(KONT) = NU_ZOOMX
         LIBCHIM_T (KONT) = TRIM(LIBCHIM)
         KONT_SEM = KONT_SEM + 1
!        ========================
!         Lit les autres Couches
!        ========================
         DO NCO=2,NCOUC_MX
            CALL DIMSEM(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC)
            IF (IERLEC /= 0) EXIT
            KONT_SEM = KONT_SEM + 1
         ENDDO
         IF (NU_ZOOMX >= 1) THEN
!           ==============================================================
!            Lecture des Gigognes : On a lu le 0 => Reste NU_ZOOMX à lire
!           ==============================================================
            DO IZO=1,NU_ZOOMX
               DO NCO=1,NCOUC_MX
                  CALL DIMSEM(NLIG, NKOL, TITSEM, IOUCON, LEC, IERLEC)
                  IF (IERLEC /= 0) EXIT
                  KONT_SEM = KONT_SEM + 1
               ENDDO
            ENDDO
         ENDIF
      ENDDO
      NB_PAQU = KONT
!     ===================
!      Fin de la routine
!     ===================
      END SUBROUTINE ANA_MULTI_SEM_2
      SUBROUTINE LECSEM7_0(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
       , IOUCON, LEC, IERLEC, NUMERR, NTOT &
       , LIRE_DXDY, LU_DXDY, DXLU, DYLU)
!=================================================================================
!   ***********
!   *LECSEM7_0*                        BRGM     B.P. 36009
!   ***********                        45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=================================================================================
!        Lecture d'une Grille de points et rangement dans le tableau FONC()
!        Version 7.0 et 8.0
!        *** Obsolète ***
!=================================================================================
!     LEC       = Unité de Lecture
!     IOUCON    = Unité Logique d'écriture sur la console    si > 0
!                 Seulement écriture des erreurs sur console si = 0
!                 Pas d'écriture                             si < 0
!     NLIG,NKOL = Nombre maxi de Lignes et de Colonnes (pour XCOL et YLIG)
!     NTOT      = Nombre maxi de places dans le tableau FONC()
!                 N.B. : Si NTOT = 0 => On ne lit pas les points
!                        mais seulement les coordonnées (Il n'y a rien dans FONC)
!     INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
!            : 1 = Inversion la première ligne lue est rangée en dernier
!                  et YLIG est inversé aussi (logiciels d'interpolation)
!     LIRE_DXDY : 0 = On ne veut pas lire de DX() et DY()
!                    (On les saute s'ils existent)
!               : 1 = On veut lire les DX() et DY() (s'ils existent)
!     En Retour :
!     TITSEM = Dernier titre lu pour la Grille (len=132)
!     LU_DXDY : 0 = On n'a pas lu de DX et DY
!             : 1 = On a lu des DX et DY
!     XCOL  = Tableau des abscisses (si LU_XY > 0)
!     YLIG  = Tableau des ordonnées (si LU_XY > 0)
!     DXLU  = DX lus si LU_DXDY > 0
!     DYLU  = DY lus si LU_DXDY > 0
!     NLIG  = Nombre de Lignes
!     NKOL  = Nombre de Colonnes
!     X0    = Abscisse du cote ouest de la colonne n°1    (si LU_XY > 0)
!     Y0    = Ordonnée du    bas     de la ligne   n°NLIG (si LU_XY > 0)
!     NTOT  = Nombre de points = NKOL * NLIG
!     FONC  = Tableau des valeurs lues
!     IERLEC =  0 Si normal
!     IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
!     IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
!     IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
!     IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
!=================================================================================
      IMPLICIT NONE
      REAL   , DIMENSION(*), INTENT(OUT) :: FONC
      REAL   , DIMENSION(*), INTENT(IN OUT) :: XCOL, YLIG
      REAL   , DIMENSION(*) :: DXLU, DYLU
      INTEGER, INTENT(IN)  :: LIRE_DXDY, INVERS, IOUCON, LEC
      INTEGER, INTENT(OUT) :: LU_DXDY, NUMERR, IERLEC
      REAL   , INTENT(IN OUT) :: X0, Y0
      INTEGER, INTENT(IN OUT) :: NLIG, NKOL, NTOT
      CHARACTER (LEN=*), INTENT(IN OUT) :: TITSEM
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=13) :: TYP_DON
      CHARACTER (LEN=7)  :: TYP_DON3
      CHARACTER (LEN=80) :: LIBCHIM
      REAL    :: DATE
      INTEGER :: IANALY, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, LU_XY
!     =======
!      Début
!     =======
      IANALY = 0
!     ====================================
!      Appel avec 1 + 9 arguments en plus
!     ====================================
      CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
      END SUBROUTINE LECSEM7_0
