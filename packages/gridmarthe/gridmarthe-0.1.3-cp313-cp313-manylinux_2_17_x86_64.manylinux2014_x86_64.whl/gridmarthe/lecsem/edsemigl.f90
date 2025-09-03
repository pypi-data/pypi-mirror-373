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
! (from MARTHE, file : edsemi.f90, convert utf-8 )
!
! MARTHE, Copyright (c) 1990-2024 BRGM
!
      SUBROUTINE EDSEMI7_0(FONC, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
       ,TITSEM, IEREDI, IOUMAI, DXLU, DYLU)
!=================================================================================
!   ***********
!   *EDSEMI7_0*                        BRGM     B.P. 36009
!   ***********                        45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 17/09/2019
!=================================================================================
!         Édition d'une Grille suivant la norme 'Grille' Version 9.0
!         avec les DXLU() et DYLU()
!         Format libre compatible Excel
!=================================================================================
!      En entrée :
!     FONC() = Tableau monodimensionnel de NLIG * NKOL valeurs à éditer
!     XCOL() = Tableaux des Abscisses des Colonnes
!     YLIG() = Tableaux des Ordonnées des Lignes
!     DXLU() = DX
!     DYLU() = DY
!              Les DXLU() et DYLU() ne seront pas écrits si (DXLU(1) <= 0.)
!                                                        ou (DYLU(1) <= 0.)
!     NLIG  = Nombre de Lignes
!     NKOL  = Nombre de Colonnes
!     X0    = Abscisse du coté ouest de la Colonne 1
!     Y0    = Ordonnée du    bas     de la Ligne   NKOL
!     INVY  = 0 : Si les Y ou DY sont donnés de haut en bas      = Modèles
!                 (La première Ligne est celle du Haut)
!             1 : Si les Y ou DY sont donnés de Bas en Haut      = Interpolation
!                 (La première Ligne est quand même celle du Haut)
!             2 : Si les Y ou DY sont donnés de Bas en Haut      = Modèle
!                 (La première Ligne est celle du Bas)             Lecture
!                                                          avec INVERS = 1
!     TITSEM = Titre (132 Caractères)
!     IOUMAI = +-Unité Logique d'édition => Écriture sur Abs(IOUMAI)
!      En retour :
!     IEREDI = 0 Si normal
!            = 1 Si problèmes (X = XP ; Y = YP)
!            = 2 Si problèmes graves (NLIG <= 0 ; NKOL <= 0 ; X < XP ; Y < YP
!=================================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NKOL, NLIG
      REAL, DIMENSION(*), INTENT(IN) :: XCOL, YLIG, FONC
      REAL, DIMENSION(NKOL), INTENT(IN) :: DXLU
      REAL, DIMENSION(NLIG), INTENT(IN) :: DYLU
      CHARACTER (LEN=*), INTENT(IN) :: TITSEM
      REAL   , INTENT(IN)  :: X0, Y0
      INTEGER, INTENT(IN)  :: INVY, IOUMAI
      INTEGER, INTENT(OUT) :: IEREDI
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=13) :: TYP_DON
      CHARACTER (LEN=7)  :: TYP_DON3
      CHARACTER (LEN=80) :: LIBCHIM = " "
      REAL    :: DATE
      INTEGER :: ISTEP, NU_ZOOMX, NU_ZOO, NCOUC_MX, N_COUCH, N_ELEMCH
!     =======
!      Début
!     =======
      ISTEP = -9999
      TYP_DON = " "
      TYP_DON3 = " "
      LIBCHIM = " "
      NU_ZOOMX = 0
      NU_ZOO = 0
      NCOUC_MX = 0
      N_COUCH = 0
      N_ELEMCH = 0
      DATE = 0.
!     =========================================================
!      Appel avec 9 Arguments en plus
!      ISTEP = -9999 est un code => Ne pas éditer ces 9 argums
!     =========================================================
      CALL EDSEMI_3(FONC, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
           ,TITSEM, IEREDI, IOUMAI &
           ,TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
           ,DATE, LIBCHIM &
           ,DXLU, DYLU)
      END SUBROUTINE EDSEMI7_0
! ///////////////////////////////////////////////////////////////////////////////////
      SUBROUTINE EDSEMI_3(FONC, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
           ,TITSEM, IEREDI, IOUMAI &
           ,TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
           ,DATE, LIBCHIM &
           ,DXLU, DYLU)
!=================================================================================
!   **********
!   *EDSEMI_3*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 17/09/2019
!=================================================================================
!         Édition d'une Grille suivant la norme 'Grille' Version 9.0
!         avec les DXLU() et DYLU()
!         Format libre compatible Excel
!=================================================================================
!      En entrée :
!     FONC() = Tableau monodimensionnel de NLIG * NKOL valeurs à éditer
!     XCOL() = Tableaux des Abscisses des Colonnes
!     YLIG() = Tableaux des Ordonnées des Lignes
!     DXLU() = DX
!     DYLU() = DY
!             Les DXLU et DYLU ne seront pas écrits si (DXLU(1) <= 0.)
!                                                   ou (DYLU(1) <= 0.)
!     NLIG  = Nombre de Lignes
!     NKOL  = Nombre de Colonnes
!     X0    = Abscisse du coté ouest de la Colonne 1
!     Y0    = Ordonnée du    bas     de la Ligne   NKOL
!     INVY  = 0 : Si les Y ou DY sont donnés de haut en bas      = Modèles
!                 (La première Ligne est celle du Haut)
!             1 : Si les Y ou DY sont donnés de Bas en Haut      = Interpolation
!                 (La première Ligne est quand même celle du Haut)
!             2 : Si les Y ou DY sont donnés de Bas en Haut      = Modèle
!                 (La première Ligne est celle du Bas)             Lecture
!                                                          avec INVERS = 1
!     TITSEM = Titre CHARACTER (132 Caractères)
!     IOUMAI = +-Unité Logique d'édition => Écriture sur Abs(IOUMAI)
!      Et aussi
!     TYP_DON  = Type de donnée (len=13)
!     TYP_DON3 = Complément du Type de donnée (len=7)
!     N_ELEMCH = Numéro associé au Type de donnée (élément chimique)
!     LIBCHIM  = Libellé complémentaire (80 caractères maxi)
!     ISTEP    = Numéro du Pas de Temps
!     N_COUCH  = Numéro de la Couche
!     NCOUC_MX = Nombre maxi de Couches
!     NU_ZOO   = Numéro du Gigogne (0 = main)
!     NU_ZOOMX = Nombre Maxi de Gigognes
!     DATE     = Date associée à la Grille
!      En retour :
!     IEREDI = 0 Si normal
!            = 1 Si problèmes (X = XP ; Y = YP)
!            = 2 Si problèmes graves (NLIG <= 0 ; NKOL <= 0 ; X < XP ; Y < YP
!=================================================================================
!      Utilise la routine : Ecrit_Opti_12Car()
!=================================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NKOL, NLIG, IOUMAI, INVY &
                             ,N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX
      REAL   , INTENT(IN)  :: DATE, X0, Y0
      REAL, DIMENSION(*), INTENT(IN) :: XCOL, YLIG, DXLU, DYLU, FONC
      CHARACTER (LEN=*) , INTENT(IN) :: TITSEM, LIBCHIM
      CHARACTER (LEN=*) , INTENT(IN) :: TYP_DON
      CHARACTER (LEN=7) , INTENT(IN) :: TYP_DON3
      INTEGER, INTENT(OUT) :: IEREDI
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE Ecrit_Opti_12Car(X , CHAR12)
         REAL   , INTENT(IN) :: X
         CHARACTER (LEN=12), INTENT(OUT) :: CHAR12
        END SUBROUTINE Ecrit_Opti_12Car
      END INTERFACE
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=80)  :: LIBCHIM80
      CHARACTER (LEN=132) :: TITR132
      CHARACTER (LEN=1)   :: EGALIT
      CHARACTER (LEN=20)  :: TYPFOR
      INTEGER :: IED_DXDY, IOUAUX, NTOT, NONFOR, IAUX1, IAUX2 &
                ,IND, IND1, IDEB, LIG, NUMY, I, K, IERRAUX
      REAL    :: AUX, XP, YP, AUXI1, AUXI2, FONPRE
      CHARACTER (LEN=25) :: LIBEL
      CHARACTER (LEN=35) :: CHAR35
      CHARACTER (LEN=12), DIMENSION(9999) :: TABCHAR12
      CHARACTER (LEN=12) :: CHARX0, CHARY0, CHARY, CHARDY
      CHARACTER (LEN=7) , DIMENSION(9999) :: TABCHAR7
      CHARACTER (LEN=7)  :: CHARAC7
      INTEGER, DIMENSION(9999) :: TABINTEG
!     =======
!      Début
!     =======
      IEREDI  = 0
      IOUAUX  = ABS(IOUMAI)
      INQUIRE (UNIT=IOUAUX, FORM=TYPFOR)
      NONFOR = 0
      IF (TYPFOR == "UNFORMATTED") NONFOR = 1
      IED_DXDY = 1
!     ==========================================================
!      Les DXLU et DYLU ne seront pas écrits si (DXLU(1) <= 0.)
!                                            ou (DYLU(1) <= 0.)
!      => Réputés inconnus
!     ==========================================================
      IF ((DXLU(1) <= 0.).OR.(DYLU(1) <= 0.)) IED_DXDY = 0
!     ====================================================================
!      Mise du titre à 132 Caractères + Transforme les "Vides" en espaces
!     ====================================================================
      TITR132 = TITSEM
      DO K=1,LEN_TRIM(TITR132)
         IF (TITR132(K:K) == ACHAR(0)) TITR132(K:K) = " "
      ENDDO
      IF ((NLIG <= 0).OR.(NKOL <= 0)) THEN
         IEREDI = 2
         print *, 'nlig or nkol <= 0'
         GO TO 999
      ENDIF
!     =========================================================
!      Vérification des  X() et  Y()
!      * Ne vérifie pas les DX() et DY()
!      * Vérifie uniquement que X(K+1) > X(K) et Y(K+1) > Y(K)
!     =========================================================
      XP = X0
      YP = Y0
      DO I=1,NKOL
         AUX = XCOL(I)
         IF (AUX <= XP) THEN
            IEREDI = MAX(IEREDI, 1)
            IF (AUX < XP) IEREDI = 2
         ENDIF
         XP = AUX
      ENDDO
      if (IEREDI == 2) then
         print *, 'Writing marthe grid Fortran error: X not sorted'
         ! GO TO 999
      endif
!     ===================================================================
!      Dans cette version : On continue si X = XP ou Y = YP (IEREDI = 1)
!                       Mais on sort si si X < XP ou Y < YP (IEREDI = 2)
!     ===================================================================
      DO I=1,NLIG
         IND = MERGE( I , NLIG-I+1 , (INVY >= 1) )
         AUX = YLIG(IND)
         IF (AUX <= YP) THEN
            IEREDI = MAX(IEREDI, 1)
            IF (AUX < YP) IEREDI = 2
         ENDIF
         YP = AUX
      ENDDO
      IF (IEREDI == 2) then
         print *, 'Writing marthe grid Fortran error: Y not sorted'
         GO TO 999
      endif
      NTOT = NLIG * NKOL
!     =========================================
!      Vérification si la Grille est constante
!     =========================================
      EGALIT = "="
      FONPRE = FONC(1)
      IF (ANY(FONC(2:NTOT) /= FONPRE)) EGALIT = " "
      SELECT CASE (NONFOR)
      CASE (1)
!        =============
!         Non-formaté
!        =============
         SELECT CASE (ISTEP)
         CASE (-9999)
            WRITE (IOUAUX) '#BINARY#'
         CASE DEFAULT
!           ===========================================
!            Édition avec Informations Supplémentaires
!           ===========================================
            SELECT CASE ( LEN_TRIM(LIBCHIM) )
            CASE (:0)
               WRITE (IOUAUX) '#BINAR2#'
            CASE (1:)
!              ======================================
!               Édition avec Libellé Supplémentaires
!              ======================================
               WRITE (IOUAUX) '#BINAR3#'
            END SELECT
         END SELECT
         WRITE (IOUAUX) TITR132
         WRITE (IOUAUX) NKOL, NLIG, X0, Y0
         IF (ISTEP /= -9999) THEN
!           =====================================================
!            Informations supplémentaires (Après NKOL, NLIG etc)
!           =====================================================
            IAUX1 = 0
            IAUX2 = 0
            AUXI1 = 0.
            AUXI2 = 0.
            WRITE (IOUAUX) TYP_DON, TYP_DON3, N_ELEMCH, ISTEP &
               ,N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX, DATE, IAUX1, IAUX2, AUXI1, AUXI2
            IF (LEN_TRIM(LIBCHIM) > 0) THEN
!              =====================================================
!               Libellé complémentaire
!               On écrit 80 caract obligatoirement : Donc LIBCHIM80
!               #BINAR3# => Indique qu'il faudra le lire
!              =====================================================
               LIBCHIM80 = LIBCHIM
               WRITE (IOUAUX) LIBCHIM80
            ENDIF
         ENDIF
         WRITE (IOUAUX) XCOL(1:NKOL)
         SELECT CASE (INVY)
         CASE (:0)
            WRITE (IOUAUX) YLIG(1:NLIG)
         CASE DEFAULT
!           ===============
!            INVY = 1 ou 2
!           ===============
            WRITE (IOUAUX) YLIG(NLIG:1:-1)
         END SELECT
!        ==========================================
!         Non-formaté : Écriture du tableau FONC()
!        ==========================================
         WRITE (IOUAUX) EGALIT
         SELECT CASE (EGALIT)
         CASE ("=")
!           ==================
!            Grille constante
!           ==================
            WRITE (IOUAUX) FONC(1)
         CASE DEFAULT
!           ================================================
!            Écriture non-formatée des valeurs de la Grille
!           ================================================
            DO LIG=1,NLIG
               IND1 = MERGE( (LIG-1)*NKOL , (NLIG-LIG)*NKOL , (INVY < 2) )
               WRITE (IOUAUX) FONC(IND1+1:IND1+NKOL)
            ENDDO
         END SELECT
         SELECT CASE (IED_DXDY)
         CASE (1:)
!           ==============================================
!            Édition des DX() et des DY() complémentaires
!           ==============================================
            WRITE (IOUAUX) DXLU(1:NKOL)
            SELECT CASE (INVY)
            CASE (:0)
               WRITE (IOUAUX) DYLU(1:NLIG)
            CASE DEFAULT
!              ===============
!               INVY = 1 ou 2
!              ===============
               WRITE (IOUAUX) DYLU(NLIG:1:-1)
            END SELECT
         CASE (:0)
!           ====================================================
!            Pas d'édition vraie des DX() et des DY()
!            Comme on est en binaire => On les écrit quand même
!            Mais avec DXLU(1) = -1 ; DYLU(1) = -1
!           ====================================================
            WRITE (IOUAUX) (-1. , I=1,NKOL)
            WRITE (IOUAUX) (-1. , I=1,NLIG)
         END SELECT
!        ====================================
!         Fini : Fin de non-formaté : Sortie
!        ====================================
         GO TO 999
      CASE DEFAULT
      END SELECT
!     =========
!      Formaté
!     =========
      WRITE (IOUAUX, "(A)") "Marthe_Grid Version=9.0"
!     =======
!      Titre
!     =======
      IF (ISTEP >= 0) THEN
         TITR132(101:) = "<>"
         IF (NU_ZOO > 0) THEN
            WRITE (CHAR35, "(I0)", IOSTAT=IERRAUX) NU_ZOO
            TITR132 = TRIM(TITR132)//" "//TRIM(CHAR35)
         ENDIF
         TITR132 = TRIM(TITR132)//" "//TRIM(TYP_DON)
         IF (TYP_DON3 /= " ") THEN
            SELECT CASE (N_ELEMCH)
            CASE (0)
               TITR132 = TRIM(TITR132)//"/"//TRIM(TYP_DON3)
            CASE DEFAULT
               WRITE (CHAR35, "(I0)", IOSTAT=IERRAUX) N_ELEMCH
               TITR132 = TRIM(TITR132)//"/"//TRIM(TYP_DON3)//"_"//TRIM(CHAR35)
            END SELECT
         ENDIF
         IF (N_COUCH > 0) THEN
            WRITE (CHAR35, "(I0)", IOSTAT=IERRAUX) N_COUCH
            TITR132 = TRIM(TITR132)//" "//TRIM(CHAR35)
         ENDIF
      ENDIF
      WRITE (IOUAUX, "(A,A)") "Title=",TRIM(TITR132)
      WRITE (IOUAUX, "(A)") "[Infos]"
      WRITE (IOUAUX, "(A,A)") "Field=",TRIM(TYP_DON)
      WRITE (IOUAUX, "(A,A)") "Type=",TRIM(TYP_DON3)
      LIBEL = "Elem_Number="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), N_ELEMCH
      LIBEL = "Name="
      WRITE (IOUAUX, "(A,A)") TRIM(LIBEL),TRIM(LIBCHIM)
      LIBEL = "Time_Step="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), ISTEP
      LIBEL = "Time="
      CHAR35 = " "
      CALL Ecrit_Opti_12Car(DATE , CHAR35)
      WRITE (IOUAUX, "(A,A)") TRIM(LIBEL),TRIM(ADJUSTL(CHAR35))
      LIBEL = "Layer="
      WRITE (IOUAUX , "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), N_COUCH
      LIBEL = "Max_Layer="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), NCOUC_MX
      LIBEL = "Nest_grid="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), NU_ZOO
      LIBEL = "Max_NestG="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), NU_ZOOMX
      WRITE (IOUAUX, "(A)") "[Structure]"
      LIBEL = "X_Left_Corner="
      CALL Ecrit_Opti_12Car(X0 , CHARX0)
      WRITE (IOUAUX, "(A,A)") TRIM(LIBEL),TRIM(ADJUSTL(CHARX0))
      LIBEL = "Y_Lower_Corner="
      CALL Ecrit_Opti_12Car(Y0 , CHARY0)
      WRITE (IOUAUX, "(A,A)") TRIM(LIBEL),TRIM(ADJUSTL(CHARY0))
      LIBEL = "Ncolumn="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), NKOL
      LIBEL = "Nrows="
      WRITE (IOUAUX, "(A,I0)" , IOSTAT=IERRAUX) TRIM(LIBEL), NLIG
      SELECT CASE (EGALIT)
      CASE (" ")
!        ==================================
!         Cas général : Champ non Constant
!        ==================================
!        =============
!         Description
!        =============
         WRITE (IOUAUX, "(A)") "[Data_Descript]"
         WRITE (IOUAUX, "(A)") "! Line 1       :   0   ,     0          , <   1 , 2 , 3 , Ncolumn   >"
         WRITE (IOUAUX, "(A)") "! Line 2       :   0   ,     0          , < X_Center_of_all_Columns >"
         WRITE (IOUAUX, "(A)") "! Line 2+1     :   1   , Y_of_Row_1     , < Field_Values_of_all_Columns >" &
                      //" , Dy_of_Row_1"
         WRITE (IOUAUX, "(A)") "! Line 2+2     :   2   , Y_of_Row_2     , < Field_Values_of_all_Columns >" &
                      //" , Dy_of_Row_2"
         WRITE (IOUAUX, "(A)") "! Line 2+Nrows : Nrows , Y_of_Row_Nrows , < Field_Values_of_all_Columns >" &
                      //" , Dy_of_Row_2"
         WRITE (IOUAUX, "(A)") "! Line 3+Nrows :   0   ,     0          , <     Dx_of_all_Columns   >"
!        ========================
!         Valeurs et Coordonnées
!        ========================
         WRITE (IOUAUX,"(A)") "[Data]"
!        =======================
!         * Numéros de colonnes
!         * Abscisses
!        =======================
         TABINTEG(1:NKOL) = (/(K, K=1,NKOL)/)
         CALL Ecrit_Integer_Min_Car(TABINTEG(1:NKOL) , TABCHAR7(1:NKOL))
         WRITE (IOUAUX, "(20000A)") "0",CHAR(9), "0",CHAR(9), (TRIM(TABCHAR7(K)),CHAR(9), K=1,NKOL)
         CALL Ecrit_Opti_12Car(XCOL(1:NKOL) , TABCHAR12(1:NKOL))
         TABCHAR12(1:NKOL) = ADJUSTL(TABCHAR12(1:NKOL))
         WRITE (IOUAUX, "(20000A)") "0",CHAR(9), "0",CHAR(9), (TRIM(TABCHAR12(K)),CHAR(9), K=1,NKOL)
         DO LIG=1,NLIG
            NUMY = MERGE( NLIG-LIG+1 , LIG , (INVY >= 1) )
            IDEB = (LIG - 1) * NKOL
            IF (INVY >= 2) IDEB = (NUMY - 1) * NKOL
            CALL Ecrit_Opti_12Car(YLIG(NUMY) , CHARY)
            CALL Ecrit_Opti_12Car(DYLU(NUMY) , CHARDY)
            CALL Ecrit_Opti_12Car(FONC(IDEB+1:IDEB+NKOL) , TABCHAR12(1:NKOL))
            TABCHAR12(1:NKOL) = ADJUSTL(TABCHAR12(1:NKOL))
            CALL Ecrit_Integer_Min_Car(LIG , CHARAC7)
            WRITE (IOUAUX, "(20000A)") TRIM(CHARAC7),CHAR(9) , TRIM(ADJUSTL(CHARY)),CHAR(9) &
                          ,(TRIM(TABCHAR12(K)) , CHAR(9), K=1,NKOL) , TRIM(ADJUSTL(CHARDY)),CHAR(9)
         ENDDO
!        =============
!         Largeurs dx
!        =============
         CALL Ecrit_Opti_12Car(DXLU(1:NKOL) , TABCHAR12(1:NKOL))
         TABCHAR12(1:NKOL) = ADJUSTL(TABCHAR12(1:NKOL))
         WRITE (IOUAUX, "(20000A)") "0",CHAR(9), "0",CHAR(9), (TRIM(TABCHAR12(K)),CHAR(9), K=1,NKOL)
         WRITE (IOUAUX, "(A)") "[End_Grid]"
      CASE ("=")
!        ================
!         Champ Constant
!        ================
!        ========================
!         Valeurs et coordonnées
!        ========================
         WRITE (IOUAUX, "(A)") "[Constant_Data]"
         LIBEL = "Uniform_Value="
         CHAR35 = " "
         CALL Ecrit_Opti_12Car(FONC(1) , CHAR35)
         WRITE (IOUAUX, "(A,A)") TRIM(LIBEL), TRIM(ADJUSTL(CHAR35))
!        =======================
!         * Numéros de colonnes
!         * Abscisses
!         * Largeurs dx
!        =======================
         WRITE (IOUAUX, "(A)") "[Num_Columns_/_x_/_dx]"
         TABINTEG(1:NKOL) = (/(K, K=1,NKOL)/)
         CALL Ecrit_Integer_Min_Car(TABINTEG(1:NKOL) , TABCHAR7(1:NKOL))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR7(K)),CHAR(9), K=1,NKOL)
         CALL Ecrit_Opti_12Car(XCOL(1:NKOL) , TABCHAR12(1:NKOL))
         TABCHAR12(1:NKOL) = ADJUSTL(TABCHAR12(1:NKOL))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR12(K)),CHAR(9), K=1,NKOL)
         CALL Ecrit_Opti_12Car(DXLU(1:NKOL) , TABCHAR12(1:NKOL))
         TABCHAR12(1:NKOL) = ADJUSTL(TABCHAR12(1:NKOL))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR12(K)),CHAR(9), K=1,NKOL)
!        =====================
!         * Numéros de lignes
!         * Ordonnées
!         * Hauteurs dy
!        =====================
         WRITE (IOUAUX,"(A)") "[Num_Rows_/_y_/_dy]"
         TABINTEG(1:NLIG) = (/(K, K=1,NLIG)/)
         CALL Ecrit_Integer_Min_Car(TABINTEG(1:NLIG) , TABCHAR7(1:NLIG))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR7(K)),CHAR(9), K=1,NLIG)
!        ======
!         YLIG
!        ======
         SELECT CASE (INVY)
         CASE (:0)
            CALL Ecrit_Opti_12Car(YLIG(1:NLIG) , TABCHAR12(1:NLIG))
         CASE DEFAULT
!           ===============
!            INVY = 1 ou 2
!           ===============
            CALL Ecrit_Opti_12Car(YLIG(NLIG:1:-1) , TABCHAR12(1:NLIG))
         END SELECT
         TABCHAR12(1:NLIG) = ADJUSTL(TABCHAR12(1:NLIG))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR12(K)),CHAR(9), K=1,NLIG)
!        ======
!         DYLU
!        ======
         SELECT CASE (INVY)
         CASE (:0)
            CALL Ecrit_Opti_12Car(DYLU(1:NLIG) , TABCHAR12(1:NLIG))
         CASE DEFAULT
!           ===============
!            INVY = 1 ou 2
!           ===============
            CALL Ecrit_Opti_12Car(DYLU(NLIG:1:-1) , TABCHAR12(1:NLIG))
         END SELECT
         TABCHAR12(1:NLIG) = ADJUSTL(TABCHAR12(1:NLIG))
         WRITE (IOUAUX, "(20000A)") (TRIM(TABCHAR12(K)),CHAR(9), K=1,NLIG)
         WRITE (IOUAUX, "(A)") "[End_Grid]"
      END SELECT
  999 CONTINUE
        CONTAINS
!       ////////
        ELEMENTAL PURE SUBROUTINE Ecrit_Integer_Min_Car(INTEG , CHARAC)
!       =======================================================================
!       ***********************
!       *Ecrit_Integer_Min_Car*            BRGM     B.P. 36009
!       ***********************            45060 Orléans Cédex
!       Auteur(s):THIERY D.
!       Date: 17/09/2019
!       =======================================================================
!        Écrit de manière optimale un entier en I0 dans un Character
!       =======================================================================
!        En entrée : INTEG  = Nombre entier
!        En sortie : CHARAC = Character contenant le nombre INTEG
!                             écrit sur le nombre mini de caractères
!       =======================================================================
        IMPLICIT NONE
        INTEGER, INTENT(IN) :: INTEG
        CHARACTER (LEN=*), INTENT(OUT) :: CHARAC
!       ========
!        Locaux
!       ========
        INTEGER :: IERR
!       =======
!        Début
!       =======
        WRITE (CHARAC, "(I0)" , IOSTAT=IERR) INTEG
        CHARAC = ADJUSTL(CHARAC)
        END SUBROUTINE Ecrit_Integer_Min_Car
      END SUBROUTINE EDSEMI_3
! ///////////////////////////////////////////////////////////////////////////////////
! (Provenance Fichier : ecrit_opti_12car.f90 )
      ELEMENTAL PURE SUBROUTINE Ecrit_Opti_12Car(X , CHAR12)
!=======================================================================
!   ******************
!   *Ecrit_Opti_12Car*                 BRGM     B.P. 36009
!   ******************                 45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 24/04/2019
!=======================================================================
!      Écrit de manière optimale un réel sur 12 Caractères
!=======================================================================
!      En entrée : X = Nombre réel
!      En sortie : CHAR12 = Character (Len=12) contenant le nombre X
!                           écrit de manière optimale
!=======================================================================
      IMPLICIT NONE
      REAL, INTENT(IN) :: X
      CHARACTER (LEN=12), INTENT(OUT) :: CHAR12
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=14) :: CHAR14
      INTEGER :: IERR, IPOS
!     =======
!      Début
!     =======
      CHAR12 = "0"
      IF (X == 0.) THEN
         CHAR12 = ADJUSTR(CHAR12)
      ELSE IF (X > 0.) THEN
         IF ((X >= 0.1).AND.(X <= 9999999.)) THEN
!           ===========================================================================
!            0.1 à 9.99999e6 => Format G12.7 (G12.8 si >= 1000001.)
!            Comme G12.7 pas standard => on écrit en G14.7 dans CHAR14, cadre à Gauche
!                                        Puis charge dans CHAR12, Puis cadre à droite
!            Pas d'exposant en e10 ou autre => Retire les 0 finaux
!           ===========================================================================
            IF (X <= 1000000.) THEN
               WRITE (CHAR14, 9001, IOSTAT=IERR) X
            ELSE
               WRITE (CHAR14, 9007, IOSTAT=IERR) X
            ENDIF
            CHAR14 = ADJUSTL(CHAR14)
!           ==============================================================
!            Sur certains ordis : 0.1 s'écrit 0.1000000E+000 => Problèmes
!           ==============================================================
            IF (CHAR14(13:14) /= "  ") THEN
               WRITE (CHAR12, 9002, IOSTAT=IERR) X
            ELSE
               CHAR12 = ADJUSTL(CHAR14)
               CHAR12 = ADJUSTR(CHAR12)
               CALL Elimine_Zeros_Finaux(CHAR12)
            ENDIF
         ELSE
!           ===========================================================
!            0 à 0.1 ou > 9.99999E6 => Format E12.5
!            => Ne pas retirer de 0 finaux
!              (car serait un exposant E10, E20 ... ou E-10, E-20 ...)
!           ===========================================================
            IF ((ABS(X) > 0.999D-98).AND.(ABS(X) < 0.999D+100)) THEN
               WRITE (CHAR12, 9002, IOSTAT=IERR) X
            ELSE
!              ======================================================
!               Exposant à 3 digits => seulement 4 chiffres décimaux
!              ======================================================
               WRITE (CHAR12, 9005, IOSTAT=IERR) X
!              ==============================================================
!               valeurs < 1E-99 ou > 1E+100 => Il faut ajouter la lettre "E"
!               qui n'apparait généralement pas ((LF7.1))
!               => Nécessaire pour exportations : Excel par exemple
!              ==============================================================
               IF (ABS(X) <= 1.001D-99) THEN
                  IPOS = INDEX(CHAR12 , "-" , BACK=.TRUE.)
               ELSE IF (ABS(X) >= 0.999D+100) THEN
                  IPOS = INDEX(CHAR12 , "+" , BACK=.TRUE.)
               ENDIF
               IF (IPOS > 1) THEN
                  SELECT CASE ( CHAR12(IPOS-1:IPOS-1) )
                  CASE ("E" , "e")
!                    ======
!                     Rien
!                    ======
                  CASE DEFAULT
                     CHAR12 = CHAR12(2:IPOS-1)//"E"//CHAR12(IPOS:)
                  END SELECT
               ENDIF
            ENDIF
         ENDIF
      ELSE IF (X < 0.) THEN
         IF ((ABS(X) >= 0.1).AND.(ABS(X) <= 9999999.)) THEN
!           ===========================================================================
!            -9.99999e6 à -0.1 => Format G13.7
!            Comme G13.7 pas standard => on écrit en G14.7 dans CHAR14, cadre à Gauche
!                                        Puis charge dans CHAR12, Puis cadre à droite
!            Pas d'exposant en e10 ou autre => Retire les 0 finaux
!           ===========================================================================
            WRITE (CHAR14, 9003, IOSTAT=IERR) X
            CHAR14 = ADJUSTL(CHAR14)
!           ===============================================================
!            Sur certains ordis : -0.1 s'écrit -0.1000000E+00 => Problèmes
!           ===============================================================
            IF (CHAR14(13:14) /= "  ") THEN
               WRITE (CHAR12, 9004, IOSTAT=IERR) X
            ELSE
               CHAR12 = ADJUSTL(CHAR14)
               CHAR12 = ADJUSTR(CHAR12)
               CALL Elimine_Zeros_Finaux(CHAR12)
            ENDIF
         ELSE
!           ===========================================================
!            < -9.99999E6 ou bien -0.1 à 0 => Format E12.4
!            => Ne pas retirer de 0 finaux
!              (car serait un exposant E10, E20 ... ou E-10, E-20 ...)
!           ===========================================================
            IF ((ABS(X) > 0.999D-98).AND.(ABS(X) < 0.999D+100)) THEN
               WRITE (CHAR12, 9004, IOSTAT=IERR) X
            ELSE
!              ======================================================
!               Exposant à 3 digits => seulement 3 chiffres décimaux
!              ======================================================
               WRITE (CHAR12, 9006, IOSTAT=IERR) X
!              ==============================================================
!               valeurs < 1E-99 ou > 1E+100 => Il faut ajouter la lettre "E"
!               qui n'apparait généralement pas ((LF7.1))
!               => Nécessaire pour exportations : Excel par exemple
!              ==============================================================
               IF (ABS(X) <= 1.001D-99) THEN
                  IPOS = INDEX(CHAR12 , "-" , BACK=.TRUE.)
               ELSE IF (ABS(X) >= 0.999D+100) THEN
                  IPOS = INDEX(CHAR12 , "+" , BACK=.TRUE.)
               ENDIF
               IF (IPOS > 1) THEN
                  SELECT CASE ( CHAR12(IPOS-1:IPOS-1) )
                  CASE ("E" , "e")
!                    ======
!                     Rien
!                    ======
                  CASE DEFAULT
                     CHAR12 = CHAR12(2:IPOS-1)//"E"//CHAR12(IPOS:)
                  END SELECT
               ENDIF
            ENDIF
         ENDIF
      ENDIF
 9001 FORMAT (G14.7)
 9002 FORMAT (1P,E12.5)
 9003 FORMAT (G14.7)
 9004 FORMAT (1P,E12.4)
 9005 FORMAT (1P,E12.4)
 9006 FORMAT (1P,E12.3)
 9007 FORMAT (G14.8)
         CONTAINS
         ELEMENTAL PURE SUBROUTINE Elimine_Zeros_Finaux(CHAR12)
!        ===========================================================
!         **********************
!         *Elimine_Zeros_Finaux*             BRGM     B.P. 36009
!         **********************             45060 Orléans Cédex
!        ==========================================================
!         Suppression des Zéros finaux (et du point décimal final)
!        ==========================================================
         IMPLICIT NONE
         CHARACTER (LEN=12), INTENT(IN OUT) :: CHAR12
!        ========
!         Locaux
!        ========
         INTEGER :: IPL, MODI
!        =======
!         Début
!        =======
         MODI = 0
         IPL = 12
         DO WHILE (IPL >= 2)
            IF (CHAR12(IPL:IPL) == "0") THEN
               CHAR12(IPL:IPL) = " "
               IPL = IPL - 1
               MODI = 1
            ELSE IF (CHAR12(IPL:IPL) == ".") THEN
               CHAR12(IPL:IPL) = " "
               MODI = 1
               EXIT
            ELSE
               EXIT
            ENDIF
         ENDDO
         IF (MODI == 1) CHAR12 = ADJUSTR(CHAR12)
         END SUBROUTINE Elimine_Zeros_Finaux
      END SUBROUTINE ECRIT_OPTI_12CAR
! (Provenance Fichier : edinca.f90 )
      ELEMENTAL PURE SUBROUTINE EDINCA_ELEM(CHARAX , X , NCAR)
!=======================================================================
!   *************
!   *EDINCA_ELEM*                      BRGM     B.P. 36009
!   *************                      45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!
!      Routines appelées :
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI qui supprime les Zéros finaux
!=================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NCAR
      REAL   , INTENT(IN) :: X
      CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE EDINCA_3_ELEM(CHARAX , X , NCAR , IEXACT , IESPAC)
         INTEGER, INTENT(IN) :: NCAR, IEXACT, IESPAC
         REAL   , INTENT(IN) :: X
         CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
        END SUBROUTINE EDINCA_3_ELEM
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER :: IEXACT,IESPAC
!     =======
!      Début
!     =======
      IEXACT = 0
      IESPAC = 0
      CALL EDINCA_3_ELEM(CHARAX , X , NCAR , IEXACT , IESPAC)
      END SUBROUTINE EDINCA_ELEM
      ELEMENTAL PURE SUBROUTINE EDINCA_ESP(CHARAX , X , NCAR)
!=======================================================================
!   ************
!   *EDINCA_ESP*                       BRGM     B.P. 36009
!   ************                       45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!      Avec Espace
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!
!      Routines appelées :
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI qui supprime les Zéros finaux
!=================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NCAR
      REAL   , INTENT(IN) :: X
      CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE EDINCA_3_ELEM(CHARAX, X, NCAR, IEXACT, IESPAC)
         INTEGER, INTENT(IN) :: NCAR, IEXACT, IESPAC
         REAL   , INTENT(IN) :: X
         CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
        END SUBROUTINE EDINCA_3_ELEM
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER :: IEXACT, IESPAC
!     =======
!      Début
!     =======
      IEXACT = 1
      IESPAC = 1
      CALL EDINCA_3_ELEM(CHARAX , X , NCAR , IEXACT , IESPAC)
      END SUBROUTINE EDINCA_ESP
      ELEMENTAL PURE SUBROUTINE EDINCA_2_ELEM(CHARAX, X, NCAR, IEXACT)
!=======================================================================
!   ***************
!   *EDINCA_2_ELEM*                    BRGM     B.P. 36009
!   ***************                    45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!      IEXACT : 0 = Classique (Arrondi possible des 0 ou 1 finaux
!                   des grands nombres et écriture en Format Expon)
!               1 = Pas d'Arrondi ; Pas de format Exponentiel
!                   sauf si nécessaire
!
!      Routines appelées :
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI qui supprime les Zéros finaux
!=================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NCAR, IEXACT
      REAL   , INTENT(IN) :: X
      CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE EDINCA_3_ELEM(CHARAX, X, NCAR, IEXACT, IESPAC)
         INTEGER, INTENT(IN) :: NCAR, IEXACT, IESPAC
         REAL   , INTENT(IN) :: X
         CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
        END SUBROUTINE EDINCA_3_ELEM
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER :: IESPAC
!     =======
!      Début
!     =======
      IESPAC = 0
      CALL EDINCA_3_ELEM(CHARAX,X , NCAR , IEXACT , IESPAC)
      END SUBROUTINE EDINCA_2_ELEM
      ELEMENTAL PURE SUBROUTINE EDINCA_3_ELEM(CHARAX , X , NCAR ,IEXACT , IESPAC)
!=======================================================================
!   ***************
!   *EDINCA_3_ELEM*                    BRGM     B.P. 36009
!   ***************                    45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!       ELEMENTAL PURE
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec le réel X écrit avec nombre de chiffre optimal
!      IEXACT : 0 = Classique (Arrondi possible des 0 ou 1 finaux
!                   des grands nombres et écriture en Format Expon)
!               1 = Pas d'Arrondi ; Pas de format Exponentiel
!                   sauf si nécessaire
!      IESPAC : 0 = Espace devant : Uniquement si nombre positif
!               1 = Toujours Espace devant
!
!      Routines appelées :
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI qui supprime les Zéros finaux
!=================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NCAR, IEXACT, IESPAC
      REAL   , INTENT(IN) :: X
      CHARACTER (LEN=*), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
         REAL   , INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
        END SUBROUTINE ZEROFI
        ELEMENTAL PURE SUBROUTINE NBRCHI(REEL, ICHIF, NPLACE)
         REAL   , INTENT(IN)  :: REEL
         INTEGER, INTENT(IN)  :: NPLACE
         INTEGER, INTENT(OUT) :: ICHIF
        END SUBROUTINE NBRCHI
      END INTERFACE
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=1), PARAMETER :: BLANC = " "
      CHARACTER (LEN=20) :: FORMAT, CHAR_LEFT
      INTEGER :: I, IPASS, NPLAMI, NPLAMA, NMANQ, NMANQN, NCARMA, NAUX, NAUX1, NAUX2 &
               , ICHIF, IER, LONG, IPOSI
      REAL    :: REAL_REEL
      REAL (KIND=8) :: REEL
!     =======
!      Début
!     =======
      CHARAX = BLANC
      IF ((NCAR > 20).OR.(NCAR <= 0)) GO TO 999
!     =====================
!      Places Mini et Maxi
!     =====================
      NPLAMI = NCAR - 1
      NPLAMA = NCAR
!     ===========================
!      Absent Positif et Négatif
!     ===========================
      NMANQ = 1
      NCARMA = MIN(NCAR , 8)
      DO I=1,NCARMA
         NMANQ = NMANQ * 10
      ENDDO
      NMANQ = NMANQ - 1
      NMANQN = 1
      IF (NCAR > 1) THEN
         NCARMA = MIN(NCAR-1 , 8)
         DO I=1,NCARMA
            NMANQN = NMANQN * 10
         ENDDO
         NMANQN = -(NMANQN - 1)
      ENDIF
!     ==================================
!      Début du calcul "ELEMENTAL PURE"
!     ==================================
      IPASS = 0
      REEL = X
      REAL_REEL = X
   10 IF ((REEL > 0.).OR.(IESPAC >= 1)) THEN
!        ============================================
!         Nombre Positif, ou bien Espace Obligatoire
!        ============================================
         IF (IPASS == 0) THEN
            IF (REEL > 0.) THEN
               IF ((REEL < 0.1).OR. &
                   (REEL > REAL(NMANQ))) GO TO 200
            ELSE IF (REEL <= 0.) THEN
               SELECT CASE (IESPAC)
               CASE (:0)
                  IF ((REEL > -0.01).OR. &
                      (REEL < REAL(NMANQN))) GO TO 200
               CASE (1:)
!                 =============
!                  Avec Espace
!                 =============
                  IF ((REEL > -0.1).OR. &
                      (REEL < REAL(NMANQN))) GO TO 200
               END SELECT
            ENDIF
         ENDIF
!        =======================================================
!         Si Réel positif : On essaie de laisser un place libre
!        =======================================================
         SELECT CASE (IESPAC)
         CASE (:0)
            CALL NBRCHI(REAL_REEL , ICHIF,NPLAMI)
         CASE (1:)
            CALL NBRCHI_FULL(REAL_REEL , ICHIF,NPLAMI)
         END SELECT
         IF (ICHIF == -1) THEN
!           ===========================================================================
!            Si pas assez de place : On remplit tous les caractères (sans place libre)
!           ===========================================================================
            SELECT CASE (IESPAC)
            CASE (:0)
               CALL NBRCHI(X , ICHIF , NPLAMA)
            CASE (1:)
               CALL NBRCHI_FULL(X , ICHIF , NPLAMA)
            END SELECT
         ENDIF
!        =====================================================================
!         Premier passage : Si impossible en flottant => Essai en Exponentiel
!        =====================================================================
         IF ((IPASS == 0).AND.(ICHIF == -1)) GO TO 200
         IF ( (IPASS <= 2).AND.(ICHIF == 0).AND.(IEXACT <= 0).AND. &
              ((REEL >= 9.999E4).OR.(REEL <= -9.999E4)) ) THEN
!           =======================================================
!            Si 0 chiffres : Voir si mieux en format exponentiel
!            C-à-d si *0000 ou *9999 ou *0001 par exemple
!               Ou si -*0000 ou -*9999 ou -*0001 par exemple
!            => Évite des résidus ... écrit 800000 ou 800001 = 8e5
!            => Mais peut perdre quelques chiffres signicatifs
!               1958400 sur 8 chiffres => 1.958E6 (perd le 4)
!            N.B. On ne le fait pas si IEXACT = 1
!           =======================================================
            NAUX1 = INT(REEL)
            NAUX2 = NAUX1 / 100 * 100
            IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
         ENDIF
      ELSE
!        ================
!         Négatif ou Nul
!        ================
         IF (IPASS == 0) THEN
            IF ((REEL > -0.01).OR. &
                (REEL < REAL(NMANQN))) GO TO 200
         ENDIF
!        ================================================
!         Réel Négatif : On ne laisse pas de place libre
!        ================================================
         CALL NBRCHI(X , ICHIF , NPLAMA)
         IF ((IPASS <= 2).AND.(ICHIF == 0).AND.(IEXACT <= 0).AND.(REEL <= -9.999E4)) THEN
!           =======================================================
!            Si 0 chiffres : Voir si mieux en format exponentiel
!            C-à-d si -*0000 ou -*9999 ou -*0001 par exemple
!            => Évite des résidus ... écrit 800000 ou 800001 = 8e5
!            => Mais peut perdre quelques chiffres signicatifs
!               1958400 sur 8 CHIF => 1.958E6 (perd le 4)
!            N.B. On ne le fait pas si IEXACT = 1
!           =======================================================
            NAUX1 = INT(REEL)
            NAUX2 = NAUX1 / 100 * 100
            IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
         ENDIF
      ENDIF
      IF (ICHIF > 0) THEN
         SELECT CASE (IESPAC)
         CASE (:0)
            CALL ZEROFI(REAL_REEL , ICHIF)
         CASE(1:)
!           ===================================================
!            Pour tenir compte du 0; dans -0.76543 ou -0.04321
!           ===================================================
            IF ((REEL > -1.).AND.(REEL < -0.01).AND.(ICHIF > 1)) ICHIF = ICHIF - 1
            CALL ZEROFI_OPTI(REEL , ICHIF)
         END SELECT
      ENDIF
      IF ( (IPASS <= 2).AND.(ICHIF == 0).AND.(IEXACT <= 0).AND. &
           ((REEL >= 9.999E4).OR.(REEL <= -9.999E4)) ) THEN
!        =================================================
!         Si 0 chiffres : Voir si mieux en Format Expon
!         C-à-d si  *0000 ou  *9999 ou  *0001 par exemple
!            ou si -*0000 ou -*9999 ou -*0001 par exemple
!        =================================================
         NAUX1 = INT(REEL)
         NAUX2 = NAUX1 / 100 * 100
         IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
      ENDIF
!     ==================
!      Calcul du Format
!     ==================
      CALL CALFOR(NCAR, ICHIF, FORMAT)
!===============
!      Écriture
!===============
      SELECT CASE (ICHIF)
      CASE (0)
!        ========
!         Entier
!        ========
         IF (ABS(REEL) < 1.E10) THEN
            NAUX = NINT(REEL)
         ELSE
!           ===================================================================
!            Si réel trop grand : On ne peut l'écrire en entier sinon overflow
!           ===================================================================
!           ==============================================
!            Absent > 0 => NMANQ  ;  Absent < 0 => NMANQN
!           ==============================================
            NAUX = MERGE( NMANQ , NMANQN , (REEL > 0.) )
         ENDIF
         WRITE (CHARAX , FORMAT) NAUX
      CASE (-1)
!        ============
!         Trop Grand
!        ============
!        ==============================================
!         Absent > 0 => NMANQ  ;  Absent < 0 => NMANQN
!        ==============================================
         NAUX = MERGE( NMANQ , NMANQN , (REEL > 0.) )
         WRITE (CHARAX , FORMAT) NAUX
      CASE DEFAULT
!        ===============
!         Réel Flottant
!        ===============
         WRITE (CHARAX , FORMAT) REEL
      END SELECT
!     ======
!      Fini
!     ======
      GO TO 998
!     =========================
!      Non-Fini => Exponentiel
!     =========================
  200 IF ((REEL > 0.).OR.(IESPAC >= 1)) THEN
!        =========================================
!         Positif ou Espace Obligatoire
!         => On essaie de laisser une Place Libre
!        =========================================
         CHARAX(1:1) = BLANC
         CALL CALEXP_OPTI(NPLAMI , CHARAX(2:NCAR) , REAL_REEL , IER , IESPAC)
         IF (IER == 0) GO TO 998
!        =========================================
!         Pas possible de laisser une place libre
!        =========================================
         CHARAX = BLANC
      ENDIF
      CALL CALEXP_OPTI(NCAR , CHARAX , REAL_REEL , IER , IESPAC)
      IPASS = IPASS + 1
      IF (IER > 0) THEN
         CHARAX = BLANC
         GO TO 10
      ENDIF
  998 IF (ABS(REEL) < 0.1) THEN
         CHAR_LEFT = ADJUSTL(CHARAX)
         IPOSI = INDEX(CHAR_LEFT , "-" ,BACK = .TRUE.)
         IF (IPOSI >= 2) THEN
            LONG = LEN_TRIM(CHAR_LEFT)
            IF ( (LONG <= NCAR-2).OR. &
                ((LONG <= NCAR-1).AND.(REEL < 0.).AND.(IESPAC <= 0)) ) THEN
!              ============================================================
!               2 espaces libres
!               ou bien 1 espace libre + réel < 0 + Pas espace obligatoire
!              ============================================================
               CHAR_LEFT = CHAR_LEFT(1:IPOSI-1)//"e"//CHAR_LEFT(IPOSI:)
               CHARAX = CHAR_LEFT
               CHARAX(1:NCAR) = ADJUSTR( CHARAX(1:NCAR) )
            ENDIF
         ENDIF
      ENDIF
  999 CONTINUE
         CONTAINS
!        ////////
         PURE SUBROUTINE CALEXP_OPTI(NCAR , NOMBCO , VALEUR , IER , IESPAC)
!        ==================================================================
!         *************
!         *CALEXP_OPTI*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Codage du nombre VALEUR  en "Format" Exponentiel
!               sur NCAR caractères --> NOMBCO
!         En Retour : NOMBCO (LEN = NCAR)
!          Si < 10-37 -->9999999 !!! Attention
!        ==================================================================
         IMPLICIT NONE
         INTEGER, INTENT(IN)  :: NCAR, IESPAC
         REAL   , INTENT(IN)  :: VALEUR
         CHARACTER (LEN=*), INTENT(IN OUT)  :: NOMBCO
         INTEGER, INTENT(OUT) :: IER
!        ============
!         Interfaces
!        ============
         INTERFACE
           ELEMENTAL PURE SUBROUTINE ZEROFI(REEL,ICHIF)
            REAL   , INTENT(IN) :: REEL
            INTEGER, INTENT(IN OUT) :: ICHIF
           END SUBROUTINE ZEROFI
         END INTERFACE
!        ========
!         Locaux
!        ========
         INTEGER, PARAMETER :: NCHMAX = 38
         CHARACTER (LEN=20) :: MANTIS, FORMAT
         CHARACTER (LEN=1)  :: LETTRE
         CHARACTER (LEN=1), PARAMETER :: POINT = '.' , PAROUV = '(' , PARFER = ')' &
                                       , MOINS = '-' ,      I = 'I' ,      F = 'F' &
                                       ,     E = 'E' ,   ZERO = '0' ,  BLANC = ' '
         CHARACTER (LEN=2), DIMENSION(NCHMAX), PARAMETER :: &
            CHIF = (/' 0', ' 1', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9' &
                   , '10', '11', '12', '13', '14', '15', '16', '17', '18', '19' &
                   , '20', '21', '22', '23', '24', '25', '26', '27', '28', '29' &
                   , '30', '31', '32', '33', '34', '35', '36', '37'/)
         CHARACTER (LEN=2) :: CHIAUX
         REAL    :: REAL_VALMAN
         REAL (KIND=8) :: ABVAL, AUX, ECHELL, VALMAN
         INTEGER :: NCAR1, K, ISIGVA, IEXPO, ISIGEX, KEXPO, NCHIF, NCARMA, IDEB, IVALMA
!        =======
!         Début
!        =======
         IER = 1
         IF ((NCAR >= NCHMAX).OR.(NCAR <= 0)) GO TO 999
         IF (VALEUR == 0.) THEN
            IF (NCAR == 1) THEN
               NOMBCO = ZERO
            ELSE
               NCAR1 = NCAR - 1
               WRITE (NOMBCO, "(20A)") (BLANC, K=1,NCAR1), ZERO
            ENDIF
            IER = 0
            GO TO 999
         ENDIF
!        ============================================
!         Calcul du nombre de chiffres de l'Exponent
!        ============================================
         ABVAL = ABS(VALEUR)
         ISIGVA = MERGE( 1 , -1 , (VALEUR >= 0.) )
         AUX = LOG10(ABVAL)
         IEXPO = INT(AUX)
         IF (ABVAL < 1.) THEN
            IEXPO  = IEXPO - 1
            ISIGEX = -1
         ELSE
            ISIGEX = +1
         ENDIF
         KEXPO = ABS(IEXPO)
         IF (KEXPO >= NCHMAX) GO TO 999
         ECHELL = 10._8 ** REAL(IEXPO)
!        =================
!         Mantisse VALMAN
!        =================
         VALMAN = VALEUR / ECHELL
         IF (ABS(VALMAN) > 9.999998) THEN
!           =======================================
!            Correction dans le cas ou la Mantisse
!            serait égale à 10 au lieu de 1
!           =======================================
            VALMAN = REAL(ISIGVA)
            IEXPO = IEXPO + 1
            KEXPO = ABS(IEXPO)
         ENDIF
         LETTRE = MERGE( MOINS , E , (ABVAL < 1.) )
!        ===================================================================
!         NCHIF est le nombre de chiffres après la virgule pour la Mantisse
!         NCHIF = -1 Pour écriture en entier
!        ===================================================================
         NCHIF  = NCAR - 4
         NCARMA = NCAR - 2
         IF (KEXPO > 9) THEN
            NCHIF  = NCHIF  - 1
            NCARMA = NCARMA - 1
         ENDIF
!        ===============================================
!         On retire un chiffre signif si nombre négatif
!        ===============================================
         NCHIF = NCHIF + (ISIGVA - 1) / 2
!        =============================================
!         Réduction des décimales si se termine par 0
!        =============================================
         IF (NCHIF > 0) THEN
            REAL_VALMAN = VALMAN
            SELECT CASE (IESPAC)
            CASE (:0)
               CALL ZEROFI(REAL_VALMAN , NCHIF)
            CASE(1:)
               CALL ZEROFI_OPTI(VALMAN , NCHIF)
            END SELECT
         ENDIF
      50 IF (NCHIF == 0) THEN
!           ============================================================
!            NCHIF = 0 => On passe en Entier (On code alors NCHIF à -1)
!           ============================================================
            NCHIF = -1
            IF (NCARMA == 2) THEN
!              =======================================================
!               Nombre entier et seulement 2 caractères :
!               On maximise la place en multipliant la mantisse par 10
!               (Si le dernier chiffre ne devient pas 0)
!                Exemple : 2.1-2 sur 4 caract ==> " 2-2" ==> 21-3
!              =======================================================
               IVALMA = NINT(VALMAN * 10._8)
               IF (MOD(IVALMA , 10) /= 0) THEN
                  VALMAN = VALMAN * 10._8
                  KEXPO  = KEXPO - ISIGEX
                  IF (NCARMA <= 1) GO TO 999
               ENDIF
            ENDIF
         ENDIF
         IF (NCHIF < -1) GO TO 999
         CHIAUX = CHIF(KEXPO+1)
         IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
         SELECT CASE (NCHIF)
         CASE (0:)
!           =====================================
!            Écriture de la mantisse en Flottant
!           =====================================
            FORMAT = PAROUV//F//CHIF(NCARMA+1)//POINT//CHIF(NCHIF+1)//PARFER
            WRITE (MANTIS, FORMAT, ERR=100) VALMAN
            GO TO 800
         CASE (-1)
!           ===================================
!            Écriture de la mantisse en Entier
!           ===================================
            IVALMA = NINT(VALMAN)
            IF (ABS(IVALMA) == 10) THEN
               IVALMA = IVALMA / 10
               KEXPO = KEXPO + ISIGEX
               CHIAUX = CHIF(KEXPO+1)
               IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
!              ==================================================================
!               Il faudrait sans doute aussi : NCARMA = NCARMA + 1
!               Pour cadrer à droite en fait on cadrera a posteriori par ADJUSTR
!              ==================================================================
            ENDIF
            FORMAT = PAROUV//I//CHIF(NCARMA+1)//PARFER
            WRITE (MANTIS, FORMAT, ERR=100) IVALMA
         END SELECT
     800 IF (KEXPO == 0) LETTRE = E
!        =============================================================
!         Concatenation de la Mantisse, de la Lettre et de l'Exposant
!        =============================================================
         NOMBCO = MANTIS(1:NCARMA)//LETTRE//CHIAUX(IDEB:2)
!        ===============================
!         Cadrage à droite par sécurité
!        ===============================
         NOMBCO = ADJUSTR(NOMBCO)
         IER = 0
         GO TO 999
     100 VALMAN = VALMAN / 10._8
         KEXPO = KEXPO + ISIGEX
         GO TO 50
     999 CONTINUE
         END SUBROUTINE CALEXP_OPTI
         PURE SUBROUTINE CALFOR(NCAR , ICHIF , FORMAT)
!        ==================================================================
!         **********
!         *CALFOR  *                         BRGM     B.P. 36009
!         **********                         45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Calcul du Format "FORMAT" pour NCAR caractères
!                                        ICHIF après la virgule
!        ==================================================================
         IMPLICIT NONE
         INTEGER, INTENT(IN) :: NCAR
         INTEGER, INTENT(IN OUT) :: ICHIF
         CHARACTER (LEN=*), INTENT(OUT) :: FORMAT
         CHARACTER (LEN=2), DIMENSION(21), PARAMETER :: &
            CHIF = (/' 0', ' 1', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9' &
                   , '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'/)
!        =======
!         Début
!        =======
         IF (NCAR <= 20) THEN
            IF (ICHIF > 0) THEN
               IF (ICHIF > NCAR-1) ICHIF = NCAR - 1
               FORMAT = "(F"//CHIF(NCAR+1)//"."//CHIF(ICHIF+1)//")"
            ELSE
               FORMAT = "(I"//CHIF(NCAR+1)//")"
            ENDIF
         ELSE
            FORMAT = " "
         ENDIF
         END SUBROUTINE CALFOR
         PURE SUBROUTINE NBRCHI_FULL(REEL , ICHIF , NPLACE)
!        ==================================================================
!         *************
!         *NBRCHI_FULL*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Calcul du nombre de chiffres : Pour éditer un nombre réel
!        ==================================================================
!         REEL   = Valeur réelle
!         NPLACE = Nombre de places maxi pour coder REEL
!           En retour :
!         ICHIF = Nombre de chiffres après la virgule 1 à ...
!               = -1 si espace trop petit
!        ==================================================================
!         N.B. Il est nécessaire d'utiliser la Double Précision
!        ==================================================================
         IMPLICIT NONE
         REAL   , INTENT(IN)  :: REEL
         INTEGER, INTENT(IN)  :: NPLACE
         INTEGER, INTENT(OUT) :: ICHIF
!        ========
!         Locaux
!        ========
         REAL (KIND=8) :: XMAX,AUX
         INTEGER :: IMANT
!        =======
!         Début
!        =======
         ICHIF = 2
         IF (REEL > 0) THEN
            XMAX = REEL
         ELSE IF (REEL < 0.) THEN
            XMAX = -10. * REEL
         ELSE IF (REEL == 0.) THEN
            GO TO 999
         ENDIF
         AUX  = LOG10(XMAX)
         IMANT = INT(AUX + 1.D-9) + 1
         IF (AUX < 0.)  IMANT = INT(AUX - 1.D-9)
         IF (IMANT <= 0) IMANT = 1
         ICHIF = NPLACE - IMANT - 1
         SELECT CASE (ICHIF)
         CASE (-1)
            ICHIF = 0
         CASE (:-2)
            ICHIF = -1
         END SELECT
     999 CONTINUE
         END SUBROUTINE NBRCHI_FULL
         PURE SUBROUTINE ZEROFI_OPTI(REEL , ICHIF)
!        ==================================================================
!         *************
!         *ZEROFI_OPTI*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Détermine s'il y a des zéros à la fin du réel à écrire a priori
!         avec ICHIF chiffres après la virgule
!          => Dans ce cas : Diminue ICHIF
!         *** Attention REEL doit être (KIND=8) ***
!        ==================================================================
         IMPLICIT NONE
         REAL (KIND=8), INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
!        ========
!         Locaux
!        ========
         CHARACTER (LEN=41) :: FORMAT
         CHARACTER (LEN=41) :: CHAR41
         CHARACTER (LEN=2)  :: CHAR2
         REAL :: REAL_TEST
         REAL :: PRECI_REAL
         REAL    (KIND=8) AUX
         INTEGER :: K, NBR_CHIF_ACCUR, IPOS_POINT, NB_CHIF_INTEG, NB_CHIF_SIGNIF
!        =======
!         Début
!        =======
         IF (ICHIF <= 0) GO TO 999
         REAL_TEST = 0.
         PRECI_REAL = PRECISION(REAL_TEST)
         NBR_CHIF_ACCUR = NINT( PRECI_REAL )
         AUX = ABS(REEL)
         IF ((AUX > 1.E8).AND.(NBR_CHIF_ACCUR < 10)) THEN
!           ===================================
!            En Simple Précision => 0 chiffres
!           ===================================
            ICHIF = 0
            GO TO 999
         ENDIF
         IF (NBR_CHIF_ACCUR < 10) THEN
!           =========================================
!            Simple précision : Arrondi : 7 chiffres
!           =========================================
!           =====================================
!            On écrit le nombre sur un CHARACTER
!           =====================================
            WRITE (CHAR2, "(I2)") ICHIF
            FORMAT = "(F41."//TRIM(ADJUSTL(CHAR2))//")"
            WRITE (CHAR41, TRIM(FORMAT)) AUX
!           ==========================================
!            Compte les chiffres de la partie entière
!           ==========================================
            IPOS_POINT = 41 - ICHIF
            NB_CHIF_INTEG = 0
            DO K=IPOS_POINT-1,1,-1
               IF (CHAR41(K:K) /= " ") THEN
                  NB_CHIF_INTEG = NB_CHIF_INTEG + 1
               ELSE
                  EXIT
               ENDIF
            ENDDO
            IF (NB_CHIF_INTEG == 1) THEN
               IF (CHAR41(IPOS_POINT-1:IPOS_POINT-1) == "0") NB_CHIF_INTEG = 0
            ENDIF
            IF (NB_CHIF_INTEG == 0) THEN
!              ========================================================
!               Pas de partie entière => Compte les 0 après la virgule
!               avant le début du nombre.
!               Compte négativement
!              ========================================================
               DO K=IPOS_POINT+1,41
                  IF (CHAR41(K:K) == "0") THEN
                     NB_CHIF_INTEG = NB_CHIF_INTEG - 1
                  ELSE
                     EXIT
                  ENDIF
               ENDDO
            ENDIF
            NB_CHIF_SIGNIF = NB_CHIF_INTEG + ICHIF
            IF (NB_CHIF_SIGNIF > 7) ICHIF = ICHIF - (NB_CHIF_SIGNIF - 7)
            ICHIF = MAX(ICHIF , 0)
            IF (ICHIF == 0) GO TO 999
         ENDIF
!        =====================================
!         On écrit le nombre sur un Character
!        =====================================
         WRITE (CHAR2, "(I2)") ICHIF
         FORMAT = "(F41."//TRIM(ADJUSTL(CHAR2))//")"
         WRITE (CHAR41, TRIM(FORMAT)) AUX
!        ===================================================
!         Retire un chiffre à chaque fois que un Zéro final
!        ===================================================
         IPOS_POINT = 41 - ICHIF
         DO K=41,IPOS_POINT-1,-1
            IF (CHAR41(K:K) == "0") THEN
               ICHIF = ICHIF - 1
            ELSE
               EXIT
            ENDIF
         ENDDO
         ICHIF = MAX(ICHIF , 0)
     999 CONTINUE
         END SUBROUTINE ZEROFI_OPTI
      END SUBROUTINE EDINCA_3_ELEM
      PURE SUBROUTINE EDINCA(CHARAX , X , NSEQ , NCAR)
!=======================================================================
!   **********
!   *EDINCA  *                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!      NSEQ   = Nombre de valeurs à traduire
!
!      Routines appelées :
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI qui supprime les Zéros finaux
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NSEQ, NCAR
      REAL, DIMENSION(NSEQ), INTENT(IN) :: X
      CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        PURE SUBROUTINE EDINCA_3(CHARAX, X, NSEQ, NCAR, IEXACT, IESPAC)
         INTEGER, INTENT(IN) :: NSEQ, NCAR, IEXACT, IESPAC
         REAL, DIMENSION(NSEQ), INTENT(IN) :: X
         CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
        END SUBROUTINE EDINCA_3
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER :: IEXACT, IESPAC
!     =======
!      Début
!     =======
      IEXACT = 0
      IESPAC = 0
      CALL EDINCA_3(CHARAX, X, NSEQ, NCAR, IEXACT, IESPAC)
      END SUBROUTINE EDINCA
      PURE SUBROUTINE EDINCA_ESP_OLD(CHARAX , X , NSEQ , NCAR)
!=======================================================================
!   ****************
!   *EDINCA_ESP_OLD*                   BRGM     B.P. 36009
!   ****************                   45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres réels sur NCAR caractéres avec décimales
!=======================================================================
!      X      = Tableau ou valeur à écrire sur 1 à 20 caractères
!      CHARAX = CHARACTER ou tableau CHARACTER (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!      NSEQ   = Nombre de valeurs à traduire
!
!      Routines appelées :
!       NBRCHI() qui calcule le Nombre de chiffres
!       CALFOR() qui calcule le Format d'écriture
!       ZEROFI() qui supprime les Zéros finaux
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NSEQ, NCAR
      REAL, DIMENSION(NSEQ), INTENT(IN) :: X
      CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        PURE SUBROUTINE EDINCA_3(CHARAX, X, NSEQ, NCAR, IEXACT, IESPAC)
         INTEGER, INTENT(IN) :: NSEQ, NCAR, IEXACT, IESPAC
         REAL, DIMENSION(NSEQ), INTENT(IN) :: X
         CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
        END SUBROUTINE EDINCA_3
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER :: IEXACT, IESPAC
!     =======
!      Début
!     =======
      IEXACT = 1
      IESPAC = 1
      CALL EDINCA_3(CHARAX, X, NSEQ, NCAR, IEXACT, IESPAC)
      END SUBROUTINE EDINCA_ESP_OLD
      SUBROUTINE EDINCA_2(CHARAX , X , NSEQ , NCAR , IEXACT)
!=======================================================================
!   **********
!   *EDINCA_2*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres Réels sur NCAR caractères avec décimales
!=======================================================================
!      X      = Tableau de NSEQ valeurs à écrire sur N caractères
!               N = 1 à 20
!      CHARAX = Tableau de NSEQ character (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!      NSEQ   = Nombre de valeurs à traduire
!      IEXACT : 0 = Classique (arrondi possible des 0 ou 1 finaux
!                   des grands nombres et écriture en format expon)
!               1 = Pas d'arrondi; PAs de format exponentiel
!                   sauf si nécessaire
!
!      Sous-Programmes:
!       NBRCHI() qui calcule le Nombre de chiffres
!       CALFOR() qui calcule le Format d'écriture
!       ZEROFI() Qui supprime les zéros finaux
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NSEQ, NCAR, IEXACT
      REAL, DIMENSION(NSEQ), INTENT(IN) :: X
      CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
!     ========
!      Locaux
!     ========
      INTEGER :: IESPAC
!     =======
!      Début
!     =======
      IESPAC = 0
      CALL EDINCA_3(CHARAX, X, NSEQ, NCAR, IEXACT, IESPAC)
      END SUBROUTINE EDINCA_2
      PURE SUBROUTINE EDINCA_3(CHARAX , X , NSEQ , NCAR , IEXACT , IESPAC)
!=======================================================================
!   **********
!   *EDINCA_3*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 22/12/2019
!=======================================================================
!      Écriture de nombres Réels sur NCAR caractères avec décimales
!=======================================================================
!      X      = Tableau de NSEQ valeurs à écrire sur N caractères
!               N = 1 à 20
!      CHARAX = Tableau de NSEQ character (LEN=*)
!               avec X écrit avec nombre de chiffre optimal
!      NSEQ   = Nombre de valeurs à traduire
!      IEXACT : 0 = Classique (arrondi possible des 0 ou 1 finaux
!                   des grands nombres et écriture en format expon)
!               1 = Pas d'arrondi; PAs de format exponentiel
!                   sauf si nécessaire
!      IESPAC : 0 = Espace devant : Uniquement si nombre positif
!               1 = Toujours espace devant
!
!      Sous-Programmes:
!       NBRCHI qui calcule le Nombre de chiffres
!       CALFOR qui calcule le Format d'écriture
!       ZEROFI Qui supprime les zéros finaux
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NSEQ, NCAR, IEXACT, IESPAC
      REAL, DIMENSION(NSEQ), INTENT(IN) :: X
      CHARACTER (LEN=*), DIMENSION(NSEQ), INTENT(OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
         REAL   , INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
        END SUBROUTINE ZEROFI
        ELEMENTAL PURE SUBROUTINE NBRCHI(REEL, ICHIF, NPLACE)
         REAL   , INTENT(IN)  :: REEL
         INTEGER, INTENT(IN)  :: NPLACE
         INTEGER, INTENT(OUT) :: ICHIF
        END SUBROUTINE NBRCHI
      END INTERFACE
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=1), PARAMETER :: BLANC = " "
      CHARACTER (LEN=20) :: FORMAT
      INTEGER :: I, IPASS, NPLAMI, NPLAMA, NMANQ, NMANQN, NCARMA, NAUX, NAUX1, NAUX2 &
                ,ICHIF, IER
      REAL    :: REAL_REEL
      REAL (KIND=8) :: REEL
!     =======
!      Début
!     =======
      CHARAX(1:NSEQ) = BLANC
      IF ((NCAR > 20).OR.(NCAR <= 0)) GO TO 999
!     =====================
!      Places mini et maxi
!     =====================
      NPLAMI = NCAR - 1
      NPLAMA = NCAR
!     ===========================
!      Absent positif et négatif
!     ===========================
      NMANQ = 1
      NCARMA = MIN(NCAR , 8)
      DO I=1,NCARMA
         NMANQ = NMANQ * 10
      ENDDO
      NMANQ = NMANQ - 1
      NMANQN = 1
      IF (NCAR > 1) THEN
         NCARMA = MIN(NCAR-1 , 8)
         DO I=1,NCARMA
            NMANQN = NMANQN * 10
         ENDDO
         NMANQN = -(NMANQN - 1)
      ENDIF
      DO I=1,NSEQ
         IPASS = 0
         REEL = X(I)
         REAL_REEL = X(I)
   10    IF ((REEL > 0.).OR.(IESPAC >= 1)) THEN
!           ============================================
!            Nombre positif, ou bien espace obligatoire
!           ============================================
            IF (IPASS == 0) THEN
               IF (REEL > 0.) THEN
                  IF ((REEL < 0.1).OR. &
                      (REEL > REAL(NMANQ))) GO TO 200
               ELSE IF (REEL <= 0.) THEN
                  IF ((REEL > -0.01).OR. &
                      (REEL < REAL(NMANQN))) GO TO 200
               ENDIF
            ENDIF
!           =====================================================
!            Si réel positif on essaie de laisser un place libre
!           =====================================================
            SELECT CASE (IESPAC)
            CASE (:0)
               CALL NBRCHI(REAL_REEL , ICHIF,NPLAMI)
            CASE (1:)
               CALL NBRCHI_FULL(REAL_REEL , ICHIF,NPLAMI)
            END SELECT
            IF (ICHIF == -1) THEN
!              ======================================================
!               Si pas assez de place on remplit tous les caractères
!               (sans place libre)
!              ======================================================
               SELECT CASE (IESPAC)
               CASE (:0)
                  CALL NBRCHI(X(I),ICHIF,NPLAMA)
               CASE (1:)
                  CALL NBRCHI_FULL(X(I),ICHIF,NPLAMA)
               END SELECT
            ENDIF
!           =====================================================================
!            Premier passage : si impossible en flottant => essai en exponentiel
!           =====================================================================
            IF ((IPASS == 0).AND.(ICHIF == -1)) GO TO 200
            IF ( (ICHIF == 0).AND.(IEXACT <= 0).AND. &
                 ((REEL >= 9.999E4).OR.(REEL <= -9.999E4)) ) THEN
!              =======================================================
!               Si 0 chiffres : voir si mieux en format exponentiel
!               c-à-d si *0000 ou *9999 ou *0001 par exemple
!                  ou si -*0000 ou -*9999 ou -*0001 par exemple
!               => Évite des résidus ... écrit 800000 ou 800001 = 8e5
!               => Mais peut perdre quelques chiffres signicatifs
!                  1958400 sur 8 chiffres => 1.958e6 (perd le 4)
!               N.B. On ne le fait pas si IEXACT = 1
!              =======================================================
               NAUX1 = INT(REEL)
               NAUX2 = NAUX1 / 100 * 100
               IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
            ENDIF
         ELSE
!           ================
!            Négatif ou nul
!           ================
            IF (IPASS == 0) THEN
               IF ((REEL > -0.01).OR. &
                   (REEL < REAL(NMANQN))) GO TO 200
            ENDIF
!           ==============================================
!            Réel négatif on ne laisse pas de place libre
!           ==============================================
            CALL NBRCHI(X(I), ICHIF, NPLAMA)
            IF ((ICHIF == 0).AND.(IEXACT <= 0).AND.(REEL <= -9.999E4)) THEN
!              =======================================================
!               Si 0 chiffres : Voir si mieux en format exponentiel
!               c-à-d si -*0000 ou -*9999 ou -*0001 par exemple
!               => Évite des résidus ... Écrit 800000 ou 800001 = 8e5
!               => Mais peut perdre quelques chiffres signicatifs
!                  1958400 sur 8 chiffres => 1.958e6 (perd le 4)
!               N.B. On ne le fait pas si IEXACT = 1
!              =======================================================
               NAUX1 = INT(REEL)
               NAUX2 = NAUX1 / 100 * 100
               IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
            ENDIF
         ENDIF
         IF (ICHIF > 0) THEN
            SELECT CASE (IESPAC)
            CASE (:0)
               CALL ZEROFI(REAL_REEL , ICHIF)
            CASE(1:)
               CALL ZEROFI_OPTI(REEL , ICHIF)
            END SELECT
         ENDIF
         IF ( (ICHIF == 0).AND.(IEXACT <= 0).AND. &
              ((REEL >= 9.999E4).OR.(REEL <= -9.999E4)) ) THEN
!           =================================================
!            Si 0 chiffres : voir si mieux en format expon
!            c-à-d si  *0000 ou  *9999 ou  *0001 par exemple
!               ou si -*0000 ou -*9999 ou -*0001 par exemple
!           =================================================
            NAUX1 = INT(REEL)
            NAUX2 = NAUX1 / 100 * 100
            IF (ABS(NAUX1 - NAUX2) <= 1) GO TO 200
         ENDIF
!        ==================
!         Calcul du format
!        ==================
         CALL CALFOR(NCAR, ICHIF, FORMAT)
!==================
!         Écriture
!==================
         SELECT CASE (ICHIF)
         CASE (0)
!           ========
!            Entier
!           ========
            IF (ABS(REEL) < 1.E10) THEN
               NAUX = NINT(REEL)
            ELSE
!              ==================================================
!               Si réel trop grand on ne peut l'écrire en Entier
!               sinon overflow
!              ==================================================
!              ==============================================
!               ABSENT > 0 => NMANQ  ;  ABSENT < 0 => NMANQN
!              ==============================================
               NAUX = MERGE( NMANQ , NMANQN , (REEL > 0.) )
            ENDIF
            WRITE (CHARAX(I), FORMAT) NAUX
         CASE (-1)
!           ============
!            Trop grand
!           ============
!           ==============================================
!            ABSENT > 0 => NMANQ  ;  ABSENT < 0 => NMANQN
!           ==============================================
            NAUX = MERGE( NMANQ , NMANQN , (REEL > 0.) )
            WRITE (CHARAX(I), FORMAT) NAUX
         CASE DEFAULT
!           ===============
!            Réel flottant
!           ===============
            WRITE (CHARAX(I), FORMAT) REEL
         END SELECT
!        ======
!         Fini
!        ======
         CYCLE
!        =========================
!         Non-fini => Exponentiel
!        =========================
  200    IF ((REEL > 0.).OR.(IESPAC >= 1)) THEN
!           =========================================
!            Positif ou espace obligatoire
!            => On essaie de laisser une place libre
!           =========================================
            CHARAX(I)(1:1) = BLANC
            CALL CALEXP_OPTI(NPLAMI, CHARAX(I)(2:NCAR), REAL_REEL, IER, IESPAC)
            IF (IER == 0) CYCLE
!           =========================================
!            Pas possible de laisser une place libre
!           =========================================
            CHARAX(I) = BLANC
         ENDIF
         CALL CALEXP_OPTI(NCAR, CHARAX(I), REAL_REEL, IER, IESPAC)
         IPASS = 1
         IF (IER > 0) THEN
            CHARAX(I) = BLANC
            GO TO 10
         ENDIF
      ENDDO
  999 CONTINUE
         CONTAINS
!        ////////
         PURE SUBROUTINE CALEXP_OPTI(NCAR , NOMBCO , VALEUR , IER , IESPAC)
!        ==================================================================
!         *************
!         *CALEXP_OPTI*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Codage du nombre valeur  en "Format" Exponentiel
!               sur NCAR caractères --> NOMBCO
!         En retour : NOMBCO (LEN = NCAR)
!          Si < 10-37 --> 9999999
!        ==================================================================
         IMPLICIT NONE
         INTEGER, INTENT(IN)  :: NCAR, IESPAC
         REAL   , INTENT(IN)  :: VALEUR
         CHARACTER (LEN=*), INTENT(IN OUT)  :: NOMBCO
         INTEGER, INTENT(OUT) :: IER
!        ============
!         Interfaces
!        ============
         INTERFACE
           ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
            REAL   , INTENT(IN) :: REEL
            INTEGER, INTENT(IN OUT) :: ICHIF
           END SUBROUTINE ZEROFI
         END INTERFACE
!        ========
!         Locaux
!        ========
         INTEGER, PARAMETER :: NCHMAX = 38
         CHARACTER (LEN=20) :: MANTIS, FORMAT
         CHARACTER (LEN=1)  :: LETTRE
         CHARACTER (LEN=1), PARAMETER :: POINT = '.' , PAROUV = '(' , PARFER = ')' &
                                       , MOINS = '-' ,      I = 'I' ,      F = 'F' &
                                       ,     E = 'E' ,   ZERO = '0' ,  BLANC = ' '
         CHARACTER (LEN=2), DIMENSION(NCHMAX), PARAMETER :: &
            CHIF = (/' 0', ' 1', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9' &
                   , '10', '11', '12', '13', '14', '15', '16', '17', '18', '19' &
                   , '20', '21', '22', '23', '24', '25', '26', '27', '28', '29' &
                   , '30', '31', '32', '33', '34', '35', '36', '37'/)
         CHARACTER (LEN=2) :: CHIAUX
!!!      REAL    :: ABVAL, AUX, ECHELL, VALMAN
         REAL    :: REAL_VALMAN
         REAL (KIND=8) :: ABVAL, AUX, ECHELL, VALMAN
         INTEGER :: NCAR1, K, ISIGVA, IEXPO, ISIGEX, KEXPO, NCHIF, NCARMA, IDEB, IVALMA
!        =======
!         Début
!        =======
         IER = 1
         IF ((NCAR >= NCHMAX).OR.(NCAR <= 0)) GO TO 999
         IF (VALEUR == 0.) THEN
            IF (NCAR == 1) THEN
               NOMBCO = ZERO
            ELSE
               NCAR1 = NCAR - 1
               WRITE (NOMBCO, "(20A)") (BLANC, K=1,NCAR1), ZERO
            ENDIF
            IER = 0
            GO TO 999
         ENDIF
!        ============================================
!         Calcul du nombre de chiffres de l'exponent
!        ============================================
         ABVAL = ABS(VALEUR)
         ISIGVA = MERGE( 1 , -1 , (VALEUR >= 0.) )
         AUX = LOG10(ABVAL)
         IEXPO = INT(AUX)
         IF (ABVAL < 1.) THEN
            IEXPO  = IEXPO - 1
            ISIGEX = -1
         ELSE
            ISIGEX = +1
         ENDIF
         KEXPO = ABS(IEXPO)
         IF (KEXPO >= NCHMAX) GO TO 999
         ECHELL = 10._8 ** REAL(IEXPO)
!        =================
!         Mantisse VALMAN
!        =================
         VALMAN = VALEUR / ECHELL
         IF (ABS(VALMAN) > 9.999998) THEN
!           =======================================
!            Correction dans le cas ou la mantisse
!            serait égale à 10 au lieu de 1
!           =======================================
            VALMAN = REAL(ISIGVA)
            IEXPO = IEXPO + 1
            KEXPO = ABS(IEXPO)
         ENDIF
         LETTRE = MERGE( MOINS , E , (ABVAL < 1.) )
!        ===================================================================
!         NCHIF est le nombre de chiffres après la virgule pour la mantisse
!         NCHIF = -1 pour écriture en entier
!        ===================================================================
         NCHIF  = NCAR - 4
         NCARMA = NCAR - 2
         IF (KEXPO > 9) THEN
            NCHIF  = NCHIF  - 1
            NCARMA = NCARMA - 1
         ENDIF
!        ===============================================
!         On retire un chiffre signif si nombre négatif
!        ===============================================
         NCHIF = NCHIF + (ISIGVA - 1) / 2
!        =============================================
!         Réduction des décimales si se termine par 0
!        =============================================
         IF (NCHIF > 0) THEN
            REAL_VALMAN = VALMAN
            SELECT CASE (IESPAC)
            CASE (:0)
               CALL ZEROFI(REAL_VALMAN , NCHIF)
            CASE(1:)
               CALL ZEROFI_OPTI(VALMAN , NCHIF)
            END SELECT
         ENDIF
      50 IF (NCHIF == 0) THEN
!           ============================================================
!            NCHIF = 0 => On passe en entier (on code alors NCHIF à -1)
!           ============================================================
            NCHIF = -1
            IF (NCARMA == 2) THEN
!              =======================================================
!               Nombre entier et seulement 2 caractères :
!               On maximise la place en multipliant la mantisse par 10
!               (si le dernier chiffre ne devient pas 0)
!                Exemple : 2.1-2 sur 4 caract ==> " 2-2" ==> 21-3
!              =======================================================
               IVALMA = NINT(VALMAN * 10._8)
               IF (MOD(IVALMA , 10) /= 0) THEN
                  VALMAN = VALMAN * 10._8
                  KEXPO  = KEXPO - ISIGEX
                  IF (NCARMA <= 1) GO TO 999
               ENDIF
            ENDIF
         ENDIF
         IF (NCHIF < -1) GO TO 999
         CHIAUX = CHIF(KEXPO+1)
         IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
         SELECT CASE (NCHIF)
         CASE (0:)
!           =====================================
!            Écriture de la mantisse en flottant
!           =====================================
            FORMAT = PAROUV//F//CHIF(NCARMA+1)//POINT//CHIF(NCHIF+1)//PARFER
            WRITE (MANTIS, FORMAT,  ERR=100) VALMAN
            GO TO 800
         CASE (-1)
!           ===================================
!            Écriture de la mantisse en entier
!           ===================================
            IVALMA = NINT(VALMAN)
            IF (ABS(IVALMA) == 10) THEN
               IVALMA = IVALMA / 10
               KEXPO = KEXPO + ISIGEX
               CHIAUX = CHIF(KEXPO+1)
               IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
!              ================================================================
!               Il faudrait éventuellement aussi : NCARMA = NCARMA + 1
!               Pour cadrer à droite en fait on cadre a posteriori par ADJUSTR
!              ================================================================
            ENDIF
            FORMAT = PAROUV//I//CHIF(NCARMA+1)//PARFER
            WRITE (MANTIS, FORMAT, ERR=100) IVALMA
         END SELECT
     800 IF (KEXPO == 0) LETTRE = E
!        ============================================================
!         Concatenation de la mantisse de la lettre et de l'exposant
!        ============================================================
         NOMBCO = MANTIS(1:NCARMA)//LETTRE//CHIAUX(IDEB:2)
!        ===============================
!         Cadrage à droite par sécurité
!        ===============================
         NOMBCO = ADJUSTR(NOMBCO)
         IER = 0
         GO TO 999
     100 VALMAN = VALMAN / 10._8
         KEXPO = KEXPO + ISIGEX
         GO TO 50
     999 CONTINUE
         END SUBROUTINE CALEXP_OPTI
         PURE SUBROUTINE CALFOR(NCAR, ICHIF, FORMAT)
!        ==================================================================
!         **********
!         *CALFOR  *                         BRGM     B.P. 36009
!         **********                         45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Calcul du format "FORMAT" pour NCAR caractères
!                                        ICHIF après virgule
!        ==================================================================
         IMPLICIT NONE
         INTEGER, INTENT(IN) :: NCAR
         INTEGER, INTENT(IN OUT) :: ICHIF
         CHARACTER (LEN=*), INTENT(OUT) :: FORMAT
         CHARACTER (LEN=2), DIMENSION(21), PARAMETER :: &
            CHIF = (/' 0', ' 1', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9' &
                   , '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'/)
!        =======
!         Début
!        =======
         IF (NCAR <= 20) THEN
            IF (ICHIF > 0) THEN
               IF (ICHIF > NCAR-1) ICHIF = NCAR - 1
               FORMAT = "(F"//CHIF(NCAR+1)//"."//CHIF(ICHIF+1)//")"
            ELSE
               FORMAT = "(I"//CHIF(NCAR+1)//")"
            ENDIF
         ELSE
            FORMAT = " "
         ENDIF
         END SUBROUTINE CALFOR
         PURE SUBROUTINE NBRCHI_FULL(REEL , ICHIF , NPLACE)
!        ==================================================================
!         *************
!         *NBRCHI_FULL*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Calcul du nombre de chiffres : Pour éditer un nombre réel
!        ==================================================================
!         REEL   = Valeur réelle
!         NPLACE = Nombre de places maxi pour coder REEL
!           EN RETOUR :
!         ICHIF = Nombre de chiffres après la virgule 1 à ...
!               = -1 si espace trop petit
!        ==================================================================
!         N.B. Il est nécessaire d'utiliser la double précision
!        ==================================================================
         IMPLICIT NONE
         REAL   , INTENT(IN)  :: REEL
         INTEGER, INTENT(IN)  :: NPLACE
         INTEGER, INTENT(OUT) :: ICHIF
!        ========
!         Locaux
!        ========
         REAL (KIND=8) :: XMAX, AUX
         INTEGER :: IMANT
!        =======
!         Début
!        =======
         ICHIF = 2
         IF (REEL > 0) THEN
            XMAX = REEL
         ELSE IF (REEL < 0.) THEN
            XMAX = -10. * REEL
         ELSE IF (REEL == 0.) THEN
            GO TO 999
         ENDIF
         AUX  = LOG10(XMAX)
         IMANT = INT(AUX + 1.D-9) + 1
         IF (AUX < 0.)  IMANT = INT(AUX - 1.D-9)
         IF (IMANT <= 0) IMANT = 1
         ICHIF = NPLACE - IMANT - 1
         SELECT CASE (ICHIF)
         CASE (-1)
            ICHIF = 0
         CASE (:-2)
            ICHIF = -1
         END SELECT
     999 CONTINUE
         END SUBROUTINE NBRCHI_FULL
         PURE SUBROUTINE ZEROFI_OPTI(REEL , ICHIF)
!        ==================================================================
!         *************
!         *ZEROFI_OPTI*                      BRGM     B.P. 36009
!         *************                      45060 Orléans Cédex
!         Date: 22/12/2019
!         Auteur(s): THIERY D.
!        ==================================================================
!         Détermine s'il y a des zéros à la fin du REEL à écrire a priori
!         avec ICHIF chiffres après la virgule
!          => Dans ce cas : Diminue ICHIF
!         *** Attention REEL doit être (KIND=8) ***
!        ==================================================================
         IMPLICIT NONE
         REAL (KIND=8), INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
!        ========
!         Locaux
!        ========
         CHARACTER (LEN=41) :: FORMAT
         CHARACTER (LEN=41) :: CHAR41
         CHARACTER (LEN=2)  :: CHAR2
         REAL :: REAL_TEST
         REAL :: PRECI_REAL
         REAL    (KIND=8) AUX
         INTEGER :: K, NBR_CHIF_ACCUR, IPOS_POINT, NB_CHIF_INTEG, NB_CHIF_SIGNIF
!        =======
!         Début
!        =======
         IF (ICHIF <= 0) GO TO 999
         REAL_TEST = 0.
         PRECI_REAL = PRECISION(REAL_TEST)
         NBR_CHIF_ACCUR = NINT( PRECI_REAL )
         AUX = ABS(REEL)
         IF ((AUX > 1.E8).AND.(NBR_CHIF_ACCUR < 10)) THEN
!           ===================================
!            En simple précision => 0 Chiffres
!           ===================================
            ICHIF = 0
            GO TO 999
         ENDIF
         IF (NBR_CHIF_ACCUR < 10) THEN
!           =========================================
!            Simple précision : Arrondi : 7 chiffres
!           =========================================
!           =====================================
!            On écrit le nombre sur un character
!           =====================================
            WRITE (CHAR2, "(I2)") ICHIF
            FORMAT = "(F41."//TRIM(ADJUSTL(CHAR2))//")"
            WRITE (CHAR41, TRIM(FORMAT)) AUX
!           ==========================================
!            Compte les chiffres de la partie entière
!           ==========================================
            IPOS_POINT = 41 - ICHIF
            NB_CHIF_INTEG = 0
            DO K=IPOS_POINT-1,1,-1
               IF (CHAR41(K:K) /= " ") THEN
                  NB_CHIF_INTEG = NB_CHIF_INTEG + 1
               ELSE
                  EXIT
               ENDIF
            ENDDO
            IF (NB_CHIF_INTEG == 1) THEN
               IF (CHAR41(IPOS_POINT-1:IPOS_POINT-1) == "0") NB_CHIF_INTEG = 0
            ENDIF
            IF (NB_CHIF_INTEG == 0) THEN
!              ========================================================
!               Pas de partie entière => Compte les 0 après la virgule
!               avant le début du nombre
!               Compte négativement
!              ========================================================
               DO K=IPOS_POINT+1,41
                  IF (CHAR41(K:K) == "0") THEN
                     NB_CHIF_INTEG = NB_CHIF_INTEG - 1
                  ELSE
                     EXIT
                  ENDIF
               ENDDO
            ENDIF
            NB_CHIF_SIGNIF = NB_CHIF_INTEG + ICHIF
            IF (NB_CHIF_SIGNIF > 7) ICHIF = ICHIF - (NB_CHIF_SIGNIF - 7)
            ICHIF = MAX(ICHIF , 0)
            IF (ICHIF == 0) GO TO 999
         ENDIF
!        =====================================
!         On écrit le nombre sur un character
!        =====================================
         WRITE (CHAR2, "(I2)") ICHIF
         FORMAT = "(F41."//TRIM(ADJUSTL(CHAR2))//")"
         WRITE (CHAR41, TRIM(FORMAT)) AUX
!        ===================================================
!         Retire un chiffre à chaque fois que un zéro final
!        ===================================================
         IPOS_POINT = 41 - ICHIF
         DO K=41,IPOS_POINT-1,-1
            IF (CHAR41(K:K) == "0") THEN
               ICHIF = ICHIF - 1
            ELSE
               EXIT
            ENDIF
         ENDDO
         ICHIF = MAX(ICHIF , 0)
     999 CONTINUE
         END SUBROUTINE ZEROFI_OPTI
      END SUBROUTINE EDINCA_3
! (Provenance Fichier : edi7ca.f90 )
      PURE SUBROUTINE EDI7CA(CHARAX, X, NSEQ)
!=========================================================================
!   **********
!   *EDI7CA  *                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Date: 07/11/2017
!=========================================================================
!      Écriture de nombres Réels sur 7 caractères avec décimales
!=========================================================================
!      X      = Tableau de NSEQ valeurs à écrire sur 7 caractères
!      CHARAX = Tableau de NSEQ character (len=7) :: avec x écrit avec un
!               nombre de chiffre optimal 1 à 4
!      NSEQ   = Nombre de valeurs à traduires
!
!      Routines :
!       NBRCHI() qui calcule le nombre de chiffres
!       ZEROFI() qui supprime les zéros finaux
!       CALEXP() Qui calcule le format en format exponentiel
!=========================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NSEQ
      REAL, DIMENSION(*), INTENT(IN) :: X
      CHARACTER (LEN=*), DIMENSION(*), INTENT(IN OUT) :: CHARAX
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
         REAL   , INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
        END SUBROUTINE ZEROFI
        ELEMENTAL PURE SUBROUTINE NBRCHI(REEL, ICHIF, NPLACE)
         REAL   , INTENT(IN)  :: REEL
         INTEGER, INTENT(IN)  :: NPLACE
         INTEGER, INTENT(OUT) :: ICHIF
        END SUBROUTINE NBRCHI
        ELEMENTAL PURE SUBROUTINE CALEXP(NCAR, NOMBCO, VALEUR, IER)
         INTEGER, INTENT(IN)  :: NCAR
         REAL   , INTENT(IN)  :: VALEUR
         CHARACTER (LEN=*), INTENT(IN OUT)  :: NOMBCO
         INTEGER, INTENT(OUT) :: IER
        END SUBROUTINE CALEXP
      END INTERFACE
!     ========
!      Locaux
!     ========
      REAL    :: REEL
      INTEGER :: NPLAMI, NPLAMA, I, NMANQ, NMANQN, IPASS, ICHIF, NAUX, IER, NCAR
!     =======
!      Début
!     =======
      NPLAMI = 6
      NPLAMA = 7
      NMANQ  = 9999999
      NMANQN = -999999
      BAL_SEQ: DO I=1,NSEQ
         IPASS = 0
         REEL = X(I)
         ICHIF = 0
   10    IF (REEL /= 0.) THEN
            IF ( (IPASS == 0).AND.((ABS(REEL) < 0.01).OR. &
                 (REEL > REAL(NMANQ )).OR. &
                 (REEL < REAL(NMANQN))) ) GO TO 200
!           =================================
!            Format normal (pas exponentiel)
!           =================================
            CALL NBRCHI(REEL,ICHIF,NPLAMI)
            IF (ICHIF == -1) CALL NBRCHI(X(I),ICHIF,NPLAMA)
            IF (ICHIF > 0) CALL ZEROFI(REEL,ICHIF)
            IF ((IPASS == 0).AND.(ICHIF == 0)) THEN
!              =======================================================
!               Si entier avec 4 zéros à la fin => Format exponentiel
!              =======================================================
               NAUX = NINT(REEL)
               IF (MODULO(NAUX , 10000) == 0) GO TO 200
            ENDIF
         ENDIF
         SELECT CASE (ICHIF)
         CASE (0)
            NAUX = NINT(REEL)
            WRITE (CHARAX(I), 9000) NAUX
         CASE (1)
            WRITE (CHARAX(I), 9001) REEL
         CASE (2)
            WRITE (CHARAX(I), 9002) REEL
         CASE (3)
            WRITE (CHARAX(I), 9003) REEL
         CASE (4:)
            WRITE (CHARAX(I), 9004) REEL
         CASE (-1)
            WRITE (CHARAX(I), 9000) NMANQ
         END SELECT
         CYCLE BAL_SEQ
!        ====================
!         Format exponentiel
!        ====================
  200    IF (REEL >= 0.) THEN
!           =============================================================
!            Si nombre > 0
!            On essaie d'écrire sur 6 caractères (en laissant un espace)
!           =============================================================
            CHARAX(I)(1:1) = ' '
            CALL CALEXP(NPLAMI,CHARAX(I)(2:7),REEL,IER)
            IF (IER == 0) CYCLE BAL_SEQ
         ENDIF
!        ======================================================
!         Nombre négatif ou échec => On écrit sur 7 caractères
!        ======================================================
         CHARAX(I) = ' '
         NCAR = NPLAMA
         CALL CALEXP(NCAR, CHARAX(I), REEL, IER)
         IPASS = 1
         IF (IER > 0) THEN
!           ================================================
!            Échec => Retour (avec IPASS = 1)
!                     On n'écrira pas en format exponentiel
!           ================================================
            CHARAX(I) = " "
            GO TO 10
         ENDIF
      ENDDO BAL_SEQ
 9000 FORMAT (I7)
 9001 FORMAT (F7.1)
 9002 FORMAT (F7.2)
 9003 FORMAT (F7.3)
 9004 FORMAT (F7.4)
      END SUBROUTINE EDI7CA
! (Provenance Fichier : nbrchi.f90 )
      ELEMENTAL PURE SUBROUTINE NBRCHI(REEL, ICHIF, NPLACE)
!=======================================================================
!   ***********
!   *NBRCHI   *                        BRGM     B.P. 36009
!   ***********                        45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 07/11/2017
!=======================================================================
!       Calcul du nombre de chiffres : Pour éditer un nombre réel
!=======================================================================
!      REEL   = Valeur réelle
!      NPLACE = Nombre de places maxi pour coder le Réel
!        En Retour :
!      ICHIF = Nombre de chiffres après la virgule 1 à 4
!            = -1 Si espace trop petit
!=======================================================================
!      N.B. Il est nécessaire d'utiliser la double précision
!=======================================================================
      IMPLICIT NONE
      REAL   , INTENT(IN)  :: REEL
      INTEGER, INTENT(IN)  :: NPLACE
      INTEGER, INTENT(OUT) :: ICHIF
!     ========
!      Locaux
!     ========
      REAL (KIND=8) :: XMAX, AUX
      INTEGER :: IMANT
!     =======
!      Début
!     =======
      ICHIF = 2
      IF (REEL > 0) THEN
         XMAX = REEL
      ELSE IF (REEL < 0.) THEN
         XMAX = -10.*REEL
      ELSE IF (REEL == 0.) THEN
         GO TO 999
      ENDIF
      AUX  = LOG10(XMAX)
      IMANT = INT(AUX + 1.D-9) + 1
      IF (AUX < 0.)  IMANT = INT(AUX - 1.D-9)
      IF (IMANT <= 0) IMANT = 1
      ICHIF = NPLACE - IMANT - 1
      SELECT CASE (ICHIF)
      CASE (-1)
         ICHIF = 0
      CASE (:-2)
         ICHIF = -1
      CASE (5:)
         ICHIF = 4
      END SELECT
  999 CONTINUE
      END SUBROUTINE NBRCHI
! (Provenance Fichier : zerofi.f90 )
      ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
!=====================================================================
!   **********
!   *ZEROFI  *                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Date: 07/11/2017
!   Auteur(s): THIERY D.
!=====================================================================
!      Détermine si zéro à la fin
!      du réel à écrire a priori avec ICHIF chiffres après la virgule
!      => Dans ce cas : Diminue ICHIF
!=====================================================================
      IMPLICIT NONE
      REAL   , INTENT(IN) :: REEL
      INTEGER, INTENT(IN OUT) :: ICHIF
!     ========
!      Locaux
!     ========
      REAL :: AUX
      INTEGER :: K, NAUX, NCHAUX
!     =======
!      Début
!     =======
      AUX = ABS(REEL)
      IF (AUX > 1.E8) THEN
!        ===================================
!         En simple précision => 0 chiffres
!        ===================================
         ICHIF = 0
         GO TO 999
      ENDIF
!     ==========================
!      On rend le nombre Entier
!     ==========================
      DO K=1,ICHIF
         AUX = AUX * 10.
      ENDDO
      IF (AUX > 1.E8) THEN
!        ===================================
!         En simple précision => 0 Chiffres
!        ===================================
         ICHIF = 0
         GO TO 999
      ENDIF
      NAUX   = NINT(AUX)
      NCHAUX = ICHIF
!     ===================================================
!      Retire un chiffre à chaque fois que un Zéro final
!     ===================================================
      DO K=1,NCHAUX
         IF (MOD(NAUX , 10) /= 0) GO TO 999
         ICHIF = ICHIF - 1
         NAUX = NAUX / 10
      ENDDO
  999 CONTINUE
      END SUBROUTINE ZEROFI
! (Provenance Fichier : calexp.f90 )
      ELEMENTAL PURE SUBROUTINE CALEXP(NCAR, NOMBCO, VALEUR, IER)
!====================================================================
!   **********
!   *CALEXP  *                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Date: 22/12/2019
!   Auteur(s): THIERY D.
!====================================================================
!      Codage du nombre "VALEUR"  en "Format" exponentiel
!            sur NCAR caractères --> NOMBCO
!      En retour : NOMBCO (LEN=NCAR)
!       Si < 10-37 --> 9999999
!====================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NCAR
      REAL   , INTENT(IN)  :: VALEUR
      CHARACTER (LEN=*), INTENT(IN OUT)  :: NOMBCO
      INTEGER, INTENT(OUT) :: IER
!     ============
!      Interfaces
!     ============
      INTERFACE
        ELEMENTAL PURE SUBROUTINE ZEROFI(REEL, ICHIF)
         REAL   , INTENT(IN) :: REEL
         INTEGER, INTENT(IN OUT) :: ICHIF
        END SUBROUTINE ZEROFI
      END INTERFACE
!     ========
!      Locaux
!     ========
      INTEGER, PARAMETER :: NCHMAX = 38
      CHARACTER (LEN=20) :: MANTIS, FORMAT
      CHARACTER (LEN=1)  :: LETTRE
      CHARACTER (LEN=1), PARAMETER :: POINT = "." , PAROUV = "(" , PARFER = ")" &
                                    , MOINS = "-" ,      I = "I" ,      F = "F" &
                                    ,     E = "E" ,   ZERO = "0" ,  BLANC = " "
      CHARACTER (LEN=2), DIMENSION(NCHMAX), PARAMETER :: &
         CHIF = (/" 0", " 1", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9" &
                , "10", "11", "12", "13", "14", "15", "16", "17", "18", "19" &
                , "20", "21", "22", "23", "24", "25", "26", "27", "28", "29" &
                , "30", "31", "32", "33", "34", "35", "36", "37"/)
      CHARACTER (LEN=2) :: CHIAUX
      REAL    :: ABVAL, AUX, ECHELL, VALMAN
      INTEGER :: NCAR1, K, ISIGVA, IEXPO, ISIGEX, KEXPO, NCHIF, NCARMA, IDEB, IVALMA
!     =======
!      Début
!     =======
      IER = 1
      IF ((NCAR >= NCHMAX).OR.(NCAR <= 0)) GO TO 999
      IF (VALEUR == 0.) THEN
         IF (NCAR == 1) THEN
            NOMBCO = ZERO
         ELSE
            NCAR1 = NCAR - 1
            WRITE (NOMBCO, "(20A)") (BLANC, K=1,NCAR1), ZERO
         ENDIF
         IER = 0
         GO TO 999
      ENDIF
!     ============================================
!      Calcul du nombre de chiffres de l'exponent
!     ============================================
      ABVAL = ABS(VALEUR)
      ISIGVA = MERGE( 1 , -1 , (VALEUR >= 0.) )
      AUX = LOG10(ABVAL)
      IEXPO = INT(AUX)
      IF (ABVAL < 1.) THEN
         IEXPO  = IEXPO - 1
         ISIGEX = -1
      ELSE
         ISIGEX = +1
      ENDIF
      KEXPO = ABS(IEXPO)
      IF (KEXPO >= NCHMAX) GO TO 999
      ECHELL = 10. ** REAL(IEXPO)
!     =================
!      Mantisse VALMAN
!     =================
      VALMAN = VALEUR / ECHELL
      IF (ABS(VALMAN) > 9.999998) THEN
!        =======================================
!         Correction dans le cas ou la mantisse
!         serait égale à 10 au lieu de 1
!        =======================================
         VALMAN = REAL(ISIGVA)
         IEXPO = IEXPO + 1
         KEXPO = ABS(IEXPO)
      ENDIF
      LETTRE = MERGE( MOINS , E , (ABVAL < 1.) )
!     ===================================================================
!      NCHIF est le nombre de chiffres après la virgule pour la mantisse
!      NCHIF = -1 pour écriture en Entier
!     ===================================================================
      NCHIF  = NCAR - 4
      NCARMA = NCAR - 2
      IF (KEXPO > 9) THEN
         NCHIF  = NCHIF  - 1
         NCARMA = NCARMA - 1
      ENDIF
!     ===============================================
!      On retire un chiffre signif si nombre négatif
!     ===============================================
      NCHIF = NCHIF + (ISIGVA - 1) / 2
!     =============================================
!      Réduction des décimales si se termine par 0
!     =============================================
      IF (NCHIF > 0) CALL ZEROFI(VALMAN, NCHIF)
   50 IF (NCHIF == 0) THEN
!        ============================================================
!         NCHIF = 0 => On passe en Entier (on code alors NCHIF à -1)
!        ============================================================
         NCHIF = -1
         IF (NCARMA == 2) THEN
!           =======================================================
!            Nombre Entier et seulement 2 caractères :
!            On maximise la place en multipliant la mantisse par 10
!            (Si le dernier chiffre ne devient pas 0)
!             Exemple : 2.1-2 sur 4 caract ==> " 2-2" ==> 21-3
!           =======================================================
            IVALMA = NINT(VALMAN * 10.)
            IF (MOD(IVALMA , 10) /= 0) THEN
               VALMAN = VALMAN * 10.
               KEXPO  = KEXPO - ISIGEX
               IF (NCARMA <= 1) GO TO 999
            ENDIF
         ENDIF
      ENDIF
      IF (NCHIF < -1) GO TO 999
      CHIAUX = CHIF(KEXPO + 1)
      IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
      SELECT CASE (NCHIF)
      CASE (0:)
!        =====================================
!         Écriture de la mantisse en Flottant
!        =====================================
         FORMAT = PAROUV//F//CHIF(NCARMA+1)//POINT//CHIF(NCHIF+1)//PARFER
         WRITE (MANTIS, FORMAT, ERR=100) VALMAN
         GO TO 800
      CASE (-1)
!        ===================================
!         Écriture de la mantisse en Entier
!        ===================================
         IVALMA = NINT(VALMAN)
         IF (ABS(IVALMA) == 10) THEN
            IVALMA = IVALMA / 10
            KEXPO = KEXPO + ISIGEX
            CHIAUX = CHIF(KEXPO+1)
            IDEB = MERGE( 1 , 2 , (KEXPO >= 10) )
!           ==================================================================
!            Il faudrait sans doute aussi : NCARMA = NCARMA + 1
!            Pour cadrer à droite en fait on cadre a posteriori par ADJUSTR()
!           ==================================================================
         ENDIF
         FORMAT = PAROUV//I//CHIF(NCARMA+1)//PARFER
         WRITE (MANTIS, FORMAT, ERR=100) IVALMA
      END SELECT
  800 IF (KEXPO == 0) LETTRE = E
!     ============================================================
!      Concaténation de la Mantisse de la Lettre et de l'exposant
!     ============================================================
      NOMBCO = MANTIS(1:NCARMA)//LETTRE//CHIAUX(IDEB:2)
!     ===============================
!      Cadrage à droite par sécurité
!     ===============================
      NOMBCO = ADJUSTR(NOMBCO)
      IER = 0
      GO TO 999
  100 VALMAN = VALMAN / 10.
      KEXPO = KEXPO + ISIGEX
      GO TO 50
  999 CONTINUE
      END SUBROUTINE CALEXP
! (Provenance Fichier : writ_ecr.f90 )
      SUBROUTINE WRIT_ECR(IOUCON, WINT_BUFF, NO_ADVANCE)
!=======================================================================
!   **********
!   *WRIT_ECR*                         BRGM     B.P. 36009
!   **********                         45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 07/11/2017
!=======================================================================
!     Écriture sur Écran
!     Version Standard : WRITE classique
!=======================================================================
      IMPLICIT NONE
      CHARACTER (LEN=80), DIMENSION(25), INTENT(IN OUT) :: WINT_BUFF
      INTEGER, INTENT(IN) :: IOUCON, NO_ADVANCE
!     ========
!      Locaux
!     ========
      INTEGER :: LIGMAX, LIGAUX, LON, LONP, LAST
!     =======
!      Début
!     =======
      LIGMAX = 25
      DO LIGAUX=1,LIGMAX
         LON = INDEX(WINT_BUFF(LIGAUX), ACHAR(0))
         IF (LON == 1) EXIT
         LAST = 0
         IF (LIGAUX == LIGMAX) THEN
            LAST = 1
         ELSE
            IF ( INDEX(WINT_BUFF(LIGAUX+1), ACHAR(0)) == 1 ) LAST = 1
         ENDIF
         IF ((NO_ADVANCE == 0).OR.(LAST == 0)) THEN
            IF (WINT_BUFF(LIGAUX)(1:1) /= "+") THEN
               WRITE (IOUCON, "(A)") TRIM(WINT_BUFF(LIGAUX))
            ELSE
!              ===================================================
!               Format ("+") => Même ligne => Ligne blanche avant
!              ===================================================
               WRITE (IOUCON, "(A)") WINT_BUFF(LIGAUX)
            ENDIF
         ELSE
!           =========================================================
!            Dernière ligne + NO_ADVANCE => Reste sur la même ligne
!            On ajoute un blanc à la fin
!           =========================================================
            LONP = LEN_TRIM(WINT_BUFF(LIGAUX))
            IF (LONP < 80) LONP = LONP + 1
            WRITE (IOUCON, "(A)", ADVANCE="NO") WINT_BUFF(LIGAUX)(1:LONP)
         ENDIF
      ENDDO
!     =================
!      Remet à ACHAR(0)
!     =================
      WINT_BUFF = ACHAR(0)
      END SUBROUTINE WRIT_ECR
