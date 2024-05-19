toc.dat                                                                                             0000600 0004000 0002000 00000117116 14622470556 0014461 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        PGDMP       6    &                 |            Analiz    15.2    15.2 h    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false         �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false         �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false         �           1262    35987    Analiz    DATABASE     j   CREATE DATABASE "Analiz" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';
    DROP DATABASE "Analiz";
                postgres    false         �            1255    36348 
   tr_aktiv()    FUNCTION     }  CREATE FUNCTION public.tr_aktiv() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT SUM(nemater_akt + res_issl_rasrab + nemater_poisk_akt + mater_poisk_akt + ostov_sredstva +
    dohod_vlog_v_mat + fin_vlog + otlog_nalog_aktiv + proch_vneob_akt) as itog_vn_akt, id
    FROM vn_aktivs WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
     GROUP BY id
 ), 
 y as (SELECT SUM(zapas + nalog_na_dob_st_po_pr_cen + debitor_zadolg + finans_vlog + deneg_sredstv 
     + proch_obor_aktiv) as itog_ob_akt, id FROM ob_aktivs WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id)
 
 INSERT INTO balans_aktiv (id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) 
 SELECT x.id, y.id, x.itog_vn_akt, y.itog_ob_akt, SUM(x.itog_vn_akt + y.itog_ob_akt) as bal 
 FROM x,y
 GROUP BY x.id, y.id, x.itog_vn_akt, y.itog_ob_akt;
 
 return NEW;
END; 
$$;
 !   DROP FUNCTION public.tr_aktiv();
       public          postgres    false                    1255    36356    tr_fin()    FUNCTION     �  CREATE FUNCTION public.tr_fin() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT pr.val_pr, pr.pr_ot_prodag, (pr.pr_ot_prodag + dohod_ot_ychast_v_dr_org + 
											   procent_k_polych - procent_k_yplat + proch_dohod - proch_rashod) 
		   as prib_do_nalog, id FROM fin_res, 
	(SELECT val.val_pr, (val.val_pr - kommerchesk_rashod - ypravl_rashod) as pr_ot_prodag FROM fin_res, 
		(SELECT (vrychka - sebest_prodag) as val_pr FROM fin_res 
 			WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year) as val 
		WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year) as pr
	WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
    GROUP BY id, pr.pr_ot_prodag, pr.val_pr
 ),
 
 y as (SELECT (tek_nalog_na_pribl - otlog_nalog_na_pribl) as nalog_na_pr, id, proch, izm_ot_nalog_ob, izm_ot_nalog_act 
	FROM nalog_na_pribl
	WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
	GROUP BY id, proch, izm_ot_nalog_ob, izm_ot_nalog_act) 
 
 INSERT INTO fin_res_rashchet (id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) 
 SELECT y.id, x.id, x.val_pr, x.pr_ot_prodag, x.prib_do_nalog, y.nalog_na_pr, (x.prib_do_nalog - y.nalog_na_pr - y.izm_ot_nalog_ob - y.izm_ot_nalog_act - y.proch) as chist_pribl
 FROM x,y
 GROUP BY y.id, x.id, x.val_pr, x.pr_ot_prodag, x.prib_do_nalog, y.nalog_na_pr, y.proch, y.izm_ot_nalog_ob, y.izm_ot_nalog_act;
 
return NEW;
END; 
$$;
    DROP FUNCTION public.tr_fin();
       public          postgres    false                     1255    36353    tr_passiv()    FUNCTION     5  CREATE FUNCTION public.tr_passiv() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT SUM(yst_kap + sob_akci + pereocenka_vn_akt + dobav_kap + reserv_kap + neraspred_prib) as itog_kap_res, id
    FROM kap_reserv WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
     GROUP BY id
 ), 
 y as (SELECT SUM(zaymn_sredstva + kredit_zadolg + dohod_bydysh_periodov + ocenoch_ob + proch_ob) as itog_kr_ob, id FROM kratkosr_obzat WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id),
   
  z as (SELECT SUM(zaymn_sredstva + otl_nalog_ob + ocenoch_ob + proch_ob) as itog_dog_ob, id FROM dolgosr_obzat WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id)
 
 
 INSERT INTO balans_passiv (id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) 
 SELECT x.id, y.id, z.id, x.itog_kap_res, y.itog_kr_ob, z.itog_dog_ob, SUM(x.itog_kap_res + y.itog_kr_ob + z.itog_dog_ob) as bal 
 FROM x,y,z
 GROUP BY x.id, y.id, z.id, x.itog_kap_res, y.itog_kr_ob, z.itog_dog_ob;
 
 return NEW;
END; 
$$;
 "   DROP FUNCTION public.tr_passiv();
       public          postgres    false                    1255    36796    trigger_ydal_user()    FUNCTION     �  CREATE FUNCTION public.trigger_ydal_user() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	
	if (select count(*) from vhod_v_acc where vhod_v_acc.id_user=OLD.id_user)>0
	then 
		delete from vhod_v_acc where vhod_v_acc.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from ob_aktivs where ob_aktivs.id_user=OLD.id_user)>0
	then 
		if (select count(*) from vn_aktivs where vn_aktivs.id_user=OLD.id_user)>0 then
			if (SELECT count(*) FROM balans_aktiv
				JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
				JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
				WHERE ob_aktivs.id_user = OLD.id_user and vn_aktivs.id_user = OLD.id_user)>0
			then 
				delete from balans_aktiv where id IN (SELECT balans_aktiv.id FROM balans_aktiv
					JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
					JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
					WHERE ob_aktivs.id_user = OLD.id_user and vn_aktivs.id_user = OLD.id_user); 
			end if;
		end if;
		delete from ob_aktivs where ob_aktivs.id_user=OLD.id_user;
		delete from vn_aktivs where vn_aktivs.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from nalog_na_pribl where nalog_na_pribl.id_user=OLD.id_user)>0
	then
		if (select count(*) from fin_res where fin_res.id_user=OLD.id_user)>0
		then 
			if (SELECT count(*) FROM fin_res_rashchet
				JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
				JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
				WHERE nalog_na_pribl.id_user = OLD.id_user and fin_res.id_user = OLD.id_user)>0
			then 
				delete from fin_res_rashchet where id IN (SELECT fin_res_rashchet.id FROM fin_res_rashchet
					JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
					JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
					WHERE nalog_na_pribl.id_user = OLD.id_user and fin_res.id_user = OLD.id_user); 
			end if;
		end if;
		delete from nalog_na_pribl where nalog_na_pribl.id_user=OLD.id_user;
		delete from fin_res where fin_res.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from dolgosr_obzat where dolgosr_obzat.id_user=OLD.id_user)>0
	then
	
		if (select count(*) from kap_reserv where kap_reserv.id_user=OLD.id_user)>0
		then 
			if (select count(*) from kratkosr_obzat where kratkosr_obzat.id_user=OLD.id_user)>0
			then 
				if (SELECT count(*) FROM balans_passiv
						JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
						JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
						JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
							WHERE dolgosr_obzat.id_user = OLD.id_user
								and kap_reserv.id_user = OLD.id_user
								and kratkosr_obzat.id_user = OLD.id_user)>0
				then 
							delete from balans_passiv where balans_passiv.id IN (SELECT balans_passiv.id FROM balans_passiv
														JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
														JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
														JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
														WHERE dolgosr_obzat.id_user = OLD.id_user
															and kap_reserv.id_user = OLD.id_user
															and kratkosr_obzat.id_user = OLD.id_user); 
				end if;
			end if;
		end if;
		delete from dolgosr_obzat where dolgosr_obzat.id_user=OLD.id_user;
		delete from kap_reserv where kap_reserv.id_user=OLD.id_user; 
		delete from kratkosr_obzat where kratkosr_obzat.id_user=OLD.id_user; 
	end if;
	
	return OLD;

END; 
$$;
 *   DROP FUNCTION public.trigger_ydal_user();
       public          postgres    false         �            1259    36055    actions    TABLE     P   CREATE TABLE public.actions (
    id bigint NOT NULL,
    name text NOT NULL
);
    DROP TABLE public.actions;
       public         heap    postgres    false         �            1259    36054    actions_id_seq    SEQUENCE     �   ALTER TABLE public.actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    221         �            1259    36047    adm    TABLE     �   CREATE TABLE public.adm (
    id_adm bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    password text NOT NULL
);
    DROP TABLE public.adm;
       public         heap    postgres    false         �            1259    36063    adm_actions    TABLE     �   CREATE TABLE public.adm_actions (
    id bigint NOT NULL,
    id_ac bigint,
    date date DEFAULT now(),
    "time" time without time zone DEFAULT now(),
    id_adm bigint
);
    DROP TABLE public.adm_actions;
       public         heap    postgres    false         �            1259    36062    adm_actions_id_seq    SEQUENCE     �   ALTER TABLE public.adm_actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    223         �            1259    36046    adm_id_adm_seq    SEQUENCE     �   ALTER TABLE public.adm ALTER COLUMN id_adm ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_id_adm_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    219         �            1259    36223    balans_aktiv    TABLE     �   CREATE TABLE public.balans_aktiv (
    id bigint NOT NULL,
    id_vn_akt bigint,
    id_ob_akt bigint,
    itog_vn numeric NOT NULL,
    itog_ob numeric NOT NULL,
    balans numeric NOT NULL
);
     DROP TABLE public.balans_aktiv;
       public         heap    postgres    false         �            1259    36222    balans_aktiv_id_seq    SEQUENCE     �   ALTER TABLE public.balans_aktiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_aktiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    229         �            1259    36281    balans_passiv    TABLE     �   CREATE TABLE public.balans_passiv (
    id bigint NOT NULL,
    id_kap bigint,
    id_krat bigint,
    id_dolg bigint,
    itog_kap numeric NOT NULL,
    itog_krat numeric NOT NULL,
    itog_dolg numeric NOT NULL,
    balans numeric NOT NULL
);
 !   DROP TABLE public.balans_passiv;
       public         heap    postgres    false         �            1259    36280    balans_passiv_id_seq    SEQUENCE     �   ALTER TABLE public.balans_passiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_passiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    237         �            1259    36268    dolgosr_obzat    TABLE       CREATE TABLE public.dolgosr_obzat (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zaymn_sredstva numeric NOT NULL,
    otl_nalog_ob numeric NOT NULL,
    ocenoch_ob numeric NOT NULL,
    proch_ob numeric NOT NULL
);
 !   DROP TABLE public.dolgosr_obzat;
       public         heap    postgres    false         �            1259    36267    dolgosr_obzat_id_seq    SEQUENCE     �   ALTER TABLE public.dolgosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.dolgosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    235         �            1259    36317    fin_res    TABLE     �  CREATE TABLE public.fin_res (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    vrychka numeric NOT NULL,
    sebest_prodag numeric NOT NULL,
    kommerchesk_rashod numeric NOT NULL,
    ypravl_rashod numeric NOT NULL,
    dohod_ot_ychast_v_dr_org numeric NOT NULL,
    procent_k_polych numeric NOT NULL,
    procent_k_yplat numeric NOT NULL,
    proch_dohod numeric NOT NULL,
    proch_rashod numeric NOT NULL
);
    DROP TABLE public.fin_res;
       public         heap    postgres    false         �            1259    36316    fin_res_id_seq    SEQUENCE     �   ALTER TABLE public.fin_res ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    241         �            1259    36330    fin_res_rashchet    TABLE       CREATE TABLE public.fin_res_rashchet (
    id bigint NOT NULL,
    id_nalog_na_pribl bigint,
    id_fin_res bigint,
    val_pr numeric NOT NULL,
    pr_ot_prodag numeric NOT NULL,
    prib_do_nalog numeric NOT NULL,
    nalog_na_pr numeric NOT NULL,
    chist_pribl numeric NOT NULL
);
 $   DROP TABLE public.fin_res_rashchet;
       public         heap    postgres    false         �            1259    36329    fin_res_rashchet_id_seq    SEQUENCE     �   ALTER TABLE public.fin_res_rashchet ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_rashchet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    243         �            1259    36242 
   kap_reserv    TABLE     Z  CREATE TABLE public.kap_reserv (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    yst_kap numeric NOT NULL,
    sob_akci numeric NOT NULL,
    pereocenka_vn_akt numeric NOT NULL,
    dobav_kap numeric NOT NULL,
    reserv_kap numeric NOT NULL,
    neraspred_prib numeric NOT NULL
);
    DROP TABLE public.kap_reserv;
       public         heap    postgres    false         �            1259    36241    kap_reserv_id_seq    SEQUENCE     �   ALTER TABLE public.kap_reserv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kap_reserv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    231         �            1259    36255    kratkosr_obzat    TABLE     H  CREATE TABLE public.kratkosr_obzat (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zaymn_sredstva numeric NOT NULL,
    kredit_zadolg numeric NOT NULL,
    dohod_bydysh_periodov numeric NOT NULL,
    ocenoch_ob numeric NOT NULL,
    proch_ob numeric NOT NULL
);
 "   DROP TABLE public.kratkosr_obzat;
       public         heap    postgres    false         �            1259    36254    kratkosr_obzat_id_seq    SEQUENCE     �   ALTER TABLE public.kratkosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kratkosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    233         �            1259    36304    nalog_na_pribl    TABLE     5  CREATE TABLE public.nalog_na_pribl (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    tek_nalog_na_pribl numeric NOT NULL,
    otlog_nalog_na_pribl numeric NOT NULL,
    izm_ot_nalog_ob numeric,
    izm_ot_nalog_act numeric,
    proch numeric
);
 "   DROP TABLE public.nalog_na_pribl;
       public         heap    postgres    false         �            1259    36303    nalog_na_pribl_id_seq    SEQUENCE     �   ALTER TABLE public.nalog_na_pribl ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.nalog_na_pribl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    239         �            1259    36210 	   ob_aktivs    TABLE     l  CREATE TABLE public.ob_aktivs (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zapas numeric NOT NULL,
    nalog_na_dob_st_po_pr_cen numeric NOT NULL,
    debitor_zadolg numeric NOT NULL,
    finans_vlog numeric NOT NULL,
    proch_obor_aktiv numeric NOT NULL,
    deneg_sredstv numeric NOT NULL
);
    DROP TABLE public.ob_aktivs;
       public         heap    postgres    false         �            1259    36209    ob_aktivs_id_seq    SEQUENCE     �   ALTER TABLE public.ob_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ob_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    227         �            1259    36026    users    TABLE     �   CREATE TABLE public.users (
    id_user bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    phone character varying(20) NOT NULL,
    password text NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false         �            1259    36025    users_id_user_seq    SEQUENCE     �   ALTER TABLE public.users ALTER COLUMN id_user ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    215         �            1259    36034 
   vhod_v_acc    TABLE     �   CREATE TABLE public.vhod_v_acc (
    id_vhod bigint NOT NULL,
    date_vhod date DEFAULT now(),
    time_vhod time without time zone DEFAULT now(),
    id_user bigint
);
    DROP TABLE public.vhod_v_acc;
       public         heap    postgres    false         �            1259    36033    vhod_v_acc_id_vhod_seq    SEQUENCE     �   ALTER TABLE public.vhod_v_acc ALTER COLUMN id_vhod ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vhod_v_acc_id_vhod_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    217         �            1259    36197 	   vn_aktivs    TABLE     $  CREATE TABLE public.vn_aktivs (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    nemater_akt numeric NOT NULL,
    res_issl_rasrab numeric NOT NULL,
    nemater_poisk_akt numeric NOT NULL,
    mater_poisk_akt numeric NOT NULL,
    ostov_sredstva numeric NOT NULL,
    dohod_vlog_v_mat numeric NOT NULL,
    fin_vlog numeric NOT NULL,
    otlog_nalog_aktiv numeric NOT NULL,
    proch_vneob_akt numeric NOT NULL,
    avans_na_kap_str numeric NOT NULL,
    nezav_str numeric NOT NULL
);
    DROP TABLE public.vn_aktivs;
       public         heap    postgres    false         �            1259    36196    vn_aktivs_id_seq    SEQUENCE     �   ALTER TABLE public.vn_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vn_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    225         �          0    36055    actions 
   TABLE DATA           +   COPY public.actions (id, name) FROM stdin;
    public          postgres    false    221       3717.dat �          0    36047    adm 
   TABLE DATA           C   COPY public.adm (id_adm, name, login, email, password) FROM stdin;
    public          postgres    false    219       3715.dat �          0    36063    adm_actions 
   TABLE DATA           F   COPY public.adm_actions (id, id_ac, date, "time", id_adm) FROM stdin;
    public          postgres    false    223       3719.dat �          0    36223    balans_aktiv 
   TABLE DATA           Z   COPY public.balans_aktiv (id, id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) FROM stdin;
    public          postgres    false    229       3725.dat �          0    36281    balans_passiv 
   TABLE DATA           m   COPY public.balans_passiv (id, id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) FROM stdin;
    public          postgres    false    237       3733.dat �          0    36268    dolgosr_obzat 
   TABLE DATA           s   COPY public.dolgosr_obzat (id, inn, id_user, year, zaymn_sredstva, otl_nalog_ob, ocenoch_ob, proch_ob) FROM stdin;
    public          postgres    false    235       3731.dat �          0    36317    fin_res 
   TABLE DATA           �   COPY public.fin_res (id, inn, id_user, year, vrychka, sebest_prodag, kommerchesk_rashod, ypravl_rashod, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, proch_rashod) FROM stdin;
    public          postgres    false    241       3737.dat �          0    36330    fin_res_rashchet 
   TABLE DATA           �   COPY public.fin_res_rashchet (id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) FROM stdin;
    public          postgres    false    243       3739.dat �          0    36242 
   kap_reserv 
   TABLE DATA           �   COPY public.kap_reserv (id, inn, id_user, year, yst_kap, sob_akci, pereocenka_vn_akt, dobav_kap, reserv_kap, neraspred_prib) FROM stdin;
    public          postgres    false    231       3727.dat �          0    36255    kratkosr_obzat 
   TABLE DATA           �   COPY public.kratkosr_obzat (id, inn, id_user, year, zaymn_sredstva, kredit_zadolg, dohod_bydysh_periodov, ocenoch_ob, proch_ob) FROM stdin;
    public          postgres    false    233       3729.dat �          0    36304    nalog_na_pribl 
   TABLE DATA           �   COPY public.nalog_na_pribl (id, inn, id_user, year, tek_nalog_na_pribl, otlog_nalog_na_pribl, izm_ot_nalog_ob, izm_ot_nalog_act, proch) FROM stdin;
    public          postgres    false    239       3735.dat �          0    36210 	   ob_aktivs 
   TABLE DATA           �   COPY public.ob_aktivs (id, inn, id_user, year, zapas, nalog_na_dob_st_po_pr_cen, debitor_zadolg, finans_vlog, proch_obor_aktiv, deneg_sredstv) FROM stdin;
    public          postgres    false    227       3723.dat           0    36026    users 
   TABLE DATA           M   COPY public.users (id_user, name, login, email, phone, password) FROM stdin;
    public          postgres    false    215       3711.dat �          0    36034 
   vhod_v_acc 
   TABLE DATA           L   COPY public.vhod_v_acc (id_vhod, date_vhod, time_vhod, id_user) FROM stdin;
    public          postgres    false    217       3713.dat �          0    36197 	   vn_aktivs 
   TABLE DATA           �   COPY public.vn_aktivs (id, inn, id_user, year, nemater_akt, res_issl_rasrab, nemater_poisk_akt, mater_poisk_akt, ostov_sredstva, dohod_vlog_v_mat, fin_vlog, otlog_nalog_aktiv, proch_vneob_akt, avans_na_kap_str, nezav_str) FROM stdin;
    public          postgres    false    225       3721.dat �           0    0    actions_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.actions_id_seq', 3, true);
          public          postgres    false    220         �           0    0    adm_actions_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.adm_actions_id_seq', 5, true);
          public          postgres    false    222         �           0    0    adm_id_adm_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.adm_id_adm_seq', 2, true);
          public          postgres    false    218         �           0    0    balans_aktiv_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.balans_aktiv_id_seq', 22, true);
          public          postgres    false    228         �           0    0    balans_passiv_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.balans_passiv_id_seq', 13, true);
          public          postgres    false    236         �           0    0    dolgosr_obzat_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.dolgosr_obzat_id_seq', 14, true);
          public          postgres    false    234         �           0    0    fin_res_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.fin_res_id_seq', 15, true);
          public          postgres    false    240         �           0    0    fin_res_rashchet_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.fin_res_rashchet_id_seq', 13, true);
          public          postgres    false    242         �           0    0    kap_reserv_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.kap_reserv_id_seq', 15, true);
          public          postgres    false    230         �           0    0    kratkosr_obzat_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.kratkosr_obzat_id_seq', 14, true);
          public          postgres    false    232         �           0    0    nalog_na_pribl_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.nalog_na_pribl_id_seq', 15, true);
          public          postgres    false    238         �           0    0    ob_aktivs_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.ob_aktivs_id_seq', 23, true);
          public          postgres    false    226         �           0    0    users_id_user_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.users_id_user_seq', 5, true);
          public          postgres    false    214         �           0    0    vhod_v_acc_id_vhod_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.vhod_v_acc_id_vhod_seq', 59, true);
          public          postgres    false    216         �           0    0    vn_aktivs_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.vn_aktivs_id_seq', 23, true);
          public          postgres    false    224         �           2606    36061    actions actions_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.actions DROP CONSTRAINT actions_pkey;
       public            postgres    false    221         �           2606    36069    adm_actions adm_actions_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_pkey;
       public            postgres    false    223         �           2606    36053    adm adm_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.adm
    ADD CONSTRAINT adm_pkey PRIMARY KEY (id_adm);
 6   ALTER TABLE ONLY public.adm DROP CONSTRAINT adm_pkey;
       public            postgres    false    219         �           2606    36229    balans_aktiv balans_aktiv_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_pkey;
       public            postgres    false    229         �           2606    36287     balans_passiv balans_passiv_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_pkey;
       public            postgres    false    237         �           2606    36274     dolgosr_obzat dolgosr_obzat_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.dolgosr_obzat DROP CONSTRAINT dolgosr_obzat_pkey;
       public            postgres    false    235         �           2606    36323    fin_res fin_res_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.fin_res DROP CONSTRAINT fin_res_pkey;
       public            postgres    false    241         �           2606    36336 &   fin_res_rashchet fin_res_rashchet_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_pkey;
       public            postgres    false    243         �           2606    36248    kap_reserv kap_reserv_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.kap_reserv DROP CONSTRAINT kap_reserv_pkey;
       public            postgres    false    231         �           2606    36261 "   kratkosr_obzat kratkosr_obzat_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.kratkosr_obzat DROP CONSTRAINT kratkosr_obzat_pkey;
       public            postgres    false    233         �           2606    36310 "   nalog_na_pribl nalog_na_pribl_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.nalog_na_pribl DROP CONSTRAINT nalog_na_pribl_pkey;
       public            postgres    false    239         �           2606    36216    ob_aktivs ob_aktivs_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.ob_aktivs DROP CONSTRAINT ob_aktivs_pkey;
       public            postgres    false    227         �           2606    36032    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    215         �           2606    36040    vhod_v_acc vhod_v_acc_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_pkey PRIMARY KEY (id_vhod);
 D   ALTER TABLE ONLY public.vhod_v_acc DROP CONSTRAINT vhod_v_acc_pkey;
       public            postgres    false    217         �           2606    36203    vn_aktivs vn_aktivs_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.vn_aktivs DROP CONSTRAINT vn_aktivs_pkey;
       public            postgres    false    225         �           2620    36352    ob_aktivs tr_aktiv    TRIGGER     j   CREATE TRIGGER tr_aktiv AFTER INSERT ON public.ob_aktivs FOR EACH ROW EXECUTE FUNCTION public.tr_aktiv();
 +   DROP TRIGGER tr_aktiv ON public.ob_aktivs;
       public          postgres    false    255    227         �           2620    36795    nalog_na_pribl tr_fin    TRIGGER     k   CREATE TRIGGER tr_fin AFTER INSERT ON public.nalog_na_pribl FOR EACH ROW EXECUTE FUNCTION public.tr_fin();
 .   DROP TRIGGER tr_fin ON public.nalog_na_pribl;
       public          postgres    false    258    239         �           2620    36354    kratkosr_obzat tr_passiv    TRIGGER     q   CREATE TRIGGER tr_passiv AFTER INSERT ON public.kratkosr_obzat FOR EACH ROW EXECUTE FUNCTION public.tr_passiv();
 1   DROP TRIGGER tr_passiv ON public.kratkosr_obzat;
       public          postgres    false    256    233         �           2620    36800    users trigger_ydal_user    TRIGGER     y   CREATE TRIGGER trigger_ydal_user BEFORE DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trigger_ydal_user();
 0   DROP TRIGGER trigger_ydal_user ON public.users;
       public          postgres    false    215    257         �           2606    36070 "   adm_actions adm_actions_id_ac_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_ac_fkey FOREIGN KEY (id_ac) REFERENCES public.actions(id);
 L   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_id_ac_fkey;
       public          postgres    false    223    221    3524         �           2606    36075 #   adm_actions adm_actions_id_adm_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_adm_fkey FOREIGN KEY (id_adm) REFERENCES public.adm(id_adm);
 M   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_id_adm_fkey;
       public          postgres    false    219    3522    223         �           2606    36235 (   balans_aktiv balans_aktiv_id_ob_akt_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_ob_akt_fkey FOREIGN KEY (id_ob_akt) REFERENCES public.ob_aktivs(id);
 R   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_id_ob_akt_fkey;
       public          postgres    false    229    227    3530         �           2606    36230 (   balans_aktiv balans_aktiv_id_vn_akt_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_vn_akt_fkey FOREIGN KEY (id_vn_akt) REFERENCES public.vn_aktivs(id);
 R   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_id_vn_akt_fkey;
       public          postgres    false    225    229    3528         �           2606    36298 (   balans_passiv balans_passiv_id_dolg_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_dolg_fkey FOREIGN KEY (id_dolg) REFERENCES public.dolgosr_obzat(id);
 R   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_dolg_fkey;
       public          postgres    false    237    3538    235         �           2606    36288 '   balans_passiv balans_passiv_id_kap_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_kap_fkey FOREIGN KEY (id_kap) REFERENCES public.kap_reserv(id);
 Q   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_kap_fkey;
       public          postgres    false    3534    237    231         �           2606    36293 (   balans_passiv balans_passiv_id_krat_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_krat_fkey FOREIGN KEY (id_krat) REFERENCES public.kratkosr_obzat(id);
 R   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_krat_fkey;
       public          postgres    false    233    237    3536         �           2606    36275 (   dolgosr_obzat dolgosr_obzat_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 R   ALTER TABLE ONLY public.dolgosr_obzat DROP CONSTRAINT dolgosr_obzat_id_user_fkey;
       public          postgres    false    215    3518    235         �           2606    36324    fin_res fin_res_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 F   ALTER TABLE ONLY public.fin_res DROP CONSTRAINT fin_res_id_user_fkey;
       public          postgres    false    241    215    3518         �           2606    36342 1   fin_res_rashchet fin_res_rashchet_id_fin_res_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_fin_res_fkey FOREIGN KEY (id_fin_res) REFERENCES public.fin_res(id);
 [   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_id_fin_res_fkey;
       public          postgres    false    243    3544    241         �           2606    36337 8   fin_res_rashchet fin_res_rashchet_id_nalog_na_pribl_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_nalog_na_pribl_fkey FOREIGN KEY (id_nalog_na_pribl) REFERENCES public.nalog_na_pribl(id);
 b   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_id_nalog_na_pribl_fkey;
       public          postgres    false    243    3542    239         �           2606    36249 "   kap_reserv kap_reserv_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 L   ALTER TABLE ONLY public.kap_reserv DROP CONSTRAINT kap_reserv_id_user_fkey;
       public          postgres    false    215    231    3518         �           2606    36262 *   kratkosr_obzat kratkosr_obzat_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 T   ALTER TABLE ONLY public.kratkosr_obzat DROP CONSTRAINT kratkosr_obzat_id_user_fkey;
       public          postgres    false    233    215    3518         �           2606    36311 *   nalog_na_pribl nalog_na_pribl_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 T   ALTER TABLE ONLY public.nalog_na_pribl DROP CONSTRAINT nalog_na_pribl_id_user_fkey;
       public          postgres    false    215    3518    239         �           2606    36217     ob_aktivs ob_aktivs_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 J   ALTER TABLE ONLY public.ob_aktivs DROP CONSTRAINT ob_aktivs_id_user_fkey;
       public          postgres    false    3518    215    227         �           2606    36041 "   vhod_v_acc vhod_v_acc_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 L   ALTER TABLE ONLY public.vhod_v_acc DROP CONSTRAINT vhod_v_acc_id_user_fkey;
       public          postgres    false    215    217    3518         �           2606    36204     vn_aktivs vn_aktivs_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 J   ALTER TABLE ONLY public.vn_aktivs DROP CONSTRAINT vn_aktivs_id_user_fkey;
       public          postgres    false    3518    215    225                                                                                                                                                                                                                                                                                                                                                                                                                                                          3717.dat                                                                                            0000600 0004000 0002000 00000000166 14622470556 0014271 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1	Добавление подписки
2	Удаление пользователя
3	Вход в аккаунт
\.


                                                                                                                                                                                                                                                                                                                                                                                                          3715.dat                                                                                            0000600 0004000 0002000 00000000257 14622470556 0014270 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1	Иван	adm1	ivanadm@mail.ru	11111
2	Адам	adm2	adam@mail.ru	pbkdf2:sha256:600000$8wyA6o9cCvzc6nVq$8a857330b7fbae81c997a4940c8075fa72e0692f37959d075c91339cb3a0210c
\.


                                                                                                                                                                                                                                                                                                                                                 3719.dat                                                                                            0000600 0004000 0002000 00000000252 14622470556 0014267 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1	3	2024-05-19	17:50:05.195397	2
2	3	2024-05-19	18:42:48.194262	2
3	3	2024-05-19	18:45:47.841103	2
4	3	2024-05-19	19:00:45.098193	2
5	2	2024-05-19	19:00:48.904247	2
\.


                                                                                                                                                                                                                                                                                                                                                      3725.dat                                                                                            0000600 0004000 0002000 00000000365 14622470556 0014271 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        14	15	15	142293900	109655104	251949004
6	7	7	143343962	84675506	228019468
7	8	8	148269343	130045843	278315186
15	16	16	155712502	93712880	249425382
16	17	17	438908	346294	785202
17	18	18	456432	546338	1002770
18	19	19	509392	847808	1357200
\.


                                                                                                                                                                                                                                                                           3733.dat                                                                                            0000600 0004000 0002000 00000000453 14622470556 0014266 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        3	5	4	4	80413461	96330009	75205534	251949004
5	7	6	6	77631674	95511092	54876702	228019468
4	6	5	5	62821276	124812362	90681548	278315186
6	8	7	7	54684843	77815039	116925500	249425382
7	9	8	8	318082	403806	63314	785202
8	10	9	9	453912	468568	80290	1002770
9	11	10	10	589863	605073	162264	1357200
\.


                                                                                                                                                                                                                     3731.dat                                                                                            0000600 0004000 0002000 00000000502 14622470556 0014257 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        4	7814148471	1	2021-12-31	70874807	4330727	0	0
6	7814148471	1	2020-12-31	50076174	4800528	0	0
5	7814148471	1	2019-12-31	85298153	5383395	0	0
7	7814148471	1	2018-12-31	110865744	6059756	0	0
8	7826108963	3	2021-12-31	19495	0	0	43819
9	7826108963	3	2022-12-31	41583	0	0	38707
10	7826108963	3	2023-12-31	138780	0	0	23484
\.


                                                                                                                                                                                              3737.dat                                                                                            0000600 0004000 0002000 00000001025 14622470556 0014266 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        8	7814148471	1	2020-12-31	468171778	338847855	101980860	2902852	0	570354	6903734	7726504	7214434
9	7814148471	1	2021-12-31	495877663	359122559	114904995	1935428	0	780313	5826333	9950123	21169137
10	7814148471	1	2018-12-31	438811980	321032078	100811586	0	0	608472	9941966	3746275	4915102
11	7814148471	1	2019-12-31	441126671	322123508	104605158	0	0	3809355	12879101	10072072	5148765
12	7826108963	3	2022-12-31	671477	69184	0	491261	0	591	8530	43221	10484
13	7826108963	3	2023-12-31	862869	131968	0	605183	0	455	14232	60255	30363
\.


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           3739.dat                                                                                            0000600 0004000 0002000 00000000435 14622470556 0014274 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        6	8	8	129323923	24440211	18618901	3137726	14810398
7	9	9	136755104	19914681	3649647	867860	2781787
8	10	10	117779902	16968316	6465995	1043627	4053757
9	11	11	119003163	14398005	10251566	2115133	8136433
10	12	12	602293	111032	135830	0	135830
11	13	13	730901	125718	141833	0	141833
\.


                                                                                                                                                                                                                                   3727.dat                                                                                            0000600 0004000 0002000 00000000563 14622470556 0014273 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        5	7814148471	1	2021-12-31	1271715	0	0	14268868	0	64872878
7	7814148471	1	2020-12-31	1271715	0	0	14268868	0	62091091
6	7814148471	1	2019-12-31	1271715	0	0	14268868	0	47280693
8	7814148471	1	2018-12-31	1271715	0	0	22145486	0	31267642
9	7826108963	3	2021-12-31	10	0	0	0	0	318072
10	7826108963	3	2022-12-31	10	0	0	0	0	453902
11	7826108963	3	2023-12-31	10	0	0	0	0	589853
\.


                                                                                                                                             3729.dat                                                                                            0000600 0004000 0002000 00000000573 14622470556 0014276 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        4	7814148471	1	2021-12-31	21506485	70876965	0	3946559	0
6	7814148471	1	2020-12-31	33024151	58421081	0	4065860	0
5	7814148471	1	2019-12-31	68442386	53961543	0	2408433	0
7	7814148471	1	2018-12-31	20819222	55367522	0	1628295	0
8	7826108963	3	2021-12-31	6343	178151	219312	0	0
9	7826108963	3	2022-12-31	17824	102252	348492	0	0
10	7826108963	3	2023-12-31	18640	282042	304391	0	0
\.


                                                                                                                                     3735.dat                                                                                            0000600 0004000 0002000 00000000434 14622470556 0014267 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        8	7814148471	1	2020-12-31	4028621	890895	0	0	670777
9	7814148471	1	2021-12-31	4236030	3368170	0	0	0
10	7814148471	1	2018-12-31	1043627	0	726017	543244	99350
11	7814148471	1	2019-12-31	3028046	912913	0	0	0
12	7826108963	3	2022-12-31	0	0	0	0	0
13	7826108963	3	2023-12-31	0	0	0	0	0
\.


                                                                                                                                                                                                                                    3723.dat                                                                                            0000600 0004000 0002000 00000000707 14622470556 0014267 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        15	7814148471	1	2021-12-31	52007547	474927	25418025	0	190073	31564532
7	7814148471	1	2020-12-31	45921771	605399	17184883	0	257969	20705484
8	7814148471	1	2019-12-31	41786459	1558384	13873006	0	59896	72768098
16	7814148471	1	2018-12-31	42688427	1557771	15977292	0	0	33489390
17	7826108963	3	2021-12-31	13895	0	179258	128000	17199	7942
18	7826108963	3	2022-12-31	17191	0	448425	34000	8610	38112
19	7826108963	3	2023-12-31	268519	0	503768	0	36363	39158
\.


                                                         3711.dat                                                                                            0000600 0004000 0002000 00000000702 14622470556 0014257 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1	Иван	test1	iva@mail.ru	+7(313)982-14-91	pbkdf2:sha256:600000$cz4PRi1scHwx5fO7$1219da3c2e9b8b03ee61b850d9d6fede119f54a4d9d446e7051703207925686f
2	Petr	test2	ivanov@mail.ru	+7(318)932-42-42	pbkdf2:sha256:600000$jpABN6aAypB52IN5$5f219a1c56f80edfe42772bb222b7163e607a5928dc5639fca812f2a7ac43ca2
3	omega	omega	omega@mail.ru	+7(823)732-31-23	pbkdf2:sha256:600000$uVGHMHY6eHEKhzK5$0aa4fad6480f6a39ddf4e535e56bde51204602048c806cccf42516fef05038b6
\.


                                                              3713.dat                                                                                            0000600 0004000 0002000 00000003430 14622470556 0014262 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        1	2023-11-19	22:17:10.166195	1
2	2023-11-19	23:31:57.22532	1
3	2023-11-20	16:00:32.571123	1
4	2023-11-20	21:39:07.229457	1
5	2023-11-20	22:46:16.208583	1
6	2023-11-21	09:59:11.232775	1
7	2023-11-22	11:12:33.750657	1
8	2023-11-22	11:14:34.796218	1
9	2023-11-22	11:46:45.842379	1
10	2023-11-29	13:24:41.751665	1
11	2023-11-29	15:09:41.436135	1
12	2023-11-29	15:49:21.814792	1
13	2023-11-30	05:37:06.759801	1
14	2023-12-04	01:16:36.556083	1
15	2023-12-04	18:02:53.475317	1
16	2023-12-06	11:17:43.834408	1
17	2023-12-06	15:57:14.810466	1
18	2023-12-06	16:52:55.969596	1
19	2023-12-06	17:43:47.31312	1
20	2023-12-06	17:46:22.866587	1
21	2023-12-06	17:56:12.61184	1
22	2023-12-08	15:45:20.704038	1
23	2024-04-03	19:26:43.343689	1
24	2024-04-29	16:20:10.886324	1
25	2024-04-29	16:27:11.521705	1
26	2024-04-29	17:54:52.331417	1
27	2024-04-29	18:34:23.200999	1
28	2024-04-29	23:02:42.238895	1
29	2024-05-02	16:02:57.565425	1
30	2024-05-02	22:48:30.947667	1
31	2024-05-04	21:33:09.210852	1
32	2024-05-05	17:00:13.074062	1
33	2024-05-06	16:06:53.271835	1
34	2024-05-07	00:39:27.849183	1
35	2024-05-07	18:01:46.816627	1
36	2024-05-07	23:31:33.257423	1
37	2024-05-09	15:21:26.965103	1
38	2024-05-11	13:00:10.457829	1
39	2024-05-11	19:57:03.409678	1
40	2024-05-11	21:56:54.213113	1
41	2024-05-13	21:53:26.445214	1
42	2024-05-15	19:20:20.829513	1
43	2024-05-15	19:41:42.648088	1
44	2024-05-15	19:43:44.02087	1
45	2024-05-16	18:30:53.418643	1
46	2024-05-17	19:16:00.288365	1
47	2024-05-17	19:16:08.344566	2
48	2024-05-17	19:16:33.664659	2
49	2024-05-18	03:55:25.931399	1
50	2024-05-18	04:56:57.726025	3
51	2024-05-18	07:04:27.309183	1
52	2024-05-18	07:30:55.777853	2
53	2024-05-18	07:31:11.615931	3
54	2024-05-18	07:37:48.027647	2
55	2024-05-18	07:37:53.218061	1
56	2024-05-18	17:16:07.145543	3
59	2024-05-19	21:13:23.287533	3
\.


                                                                                                                                                                                                                                        3721.dat                                                                                            0000600 0004000 0002000 00000001036 14622470556 0014261 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        15	7814148471	1	2021-12-31	49236	0	0	0	125438177	0	7685074	3857573	5263840	0	0
7	7814148471	1	2020-12-31	21475	0	0	0	134483922	0	1169839	959204	6709522	1232269	3613741
8	7814148471	1	2019-12-31	18266	0	0	0	134365744	0	828587	651176	12405570	6859978	3675924
16	7814148471	1	2018-12-31	22743	0	0	0	142567789	0	251556	414624	12455790	0	0
17	7826108963	3	2021-12-31	183194	189693	0	0	65771	0	250	0	0	0	0
18	7826108963	3	2022-12-31	340390	50277	0	0	42674	22841	250	0	0	0	0
19	7826108963	3	2023-12-31	353674	107923	0	0	24703	22842	250	0	0	0	0
\.


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  restore.sql                                                                                         0000600 0004000 0002000 00000103652 14622470556 0015406 0                                                                                                    ustar 00postgres                        postgres                        0000000 0000000                                                                                                                                                                        --
-- NOTE:
--
-- File paths need to be edited. Search for $$PATH$$ and
-- replace it with the path to the directory containing
-- the extracted data files.
--
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE "Analiz";
--
-- Name: Analiz; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "Analiz" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';


ALTER DATABASE "Analiz" OWNER TO postgres;

\connect "Analiz"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tr_aktiv(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tr_aktiv() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT SUM(nemater_akt + res_issl_rasrab + nemater_poisk_akt + mater_poisk_akt + ostov_sredstva +
    dohod_vlog_v_mat + fin_vlog + otlog_nalog_aktiv + proch_vneob_akt) as itog_vn_akt, id
    FROM vn_aktivs WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
     GROUP BY id
 ), 
 y as (SELECT SUM(zapas + nalog_na_dob_st_po_pr_cen + debitor_zadolg + finans_vlog + deneg_sredstv 
     + proch_obor_aktiv) as itog_ob_akt, id FROM ob_aktivs WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id)
 
 INSERT INTO balans_aktiv (id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) 
 SELECT x.id, y.id, x.itog_vn_akt, y.itog_ob_akt, SUM(x.itog_vn_akt + y.itog_ob_akt) as bal 
 FROM x,y
 GROUP BY x.id, y.id, x.itog_vn_akt, y.itog_ob_akt;
 
 return NEW;
END; 
$$;


ALTER FUNCTION public.tr_aktiv() OWNER TO postgres;

--
-- Name: tr_fin(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tr_fin() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT pr.val_pr, pr.pr_ot_prodag, (pr.pr_ot_prodag + dohod_ot_ychast_v_dr_org + 
											   procent_k_polych - procent_k_yplat + proch_dohod - proch_rashod) 
		   as prib_do_nalog, id FROM fin_res, 
	(SELECT val.val_pr, (val.val_pr - kommerchesk_rashod - ypravl_rashod) as pr_ot_prodag FROM fin_res, 
		(SELECT (vrychka - sebest_prodag) as val_pr FROM fin_res 
 			WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year) as val 
		WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year) as pr
	WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
    GROUP BY id, pr.pr_ot_prodag, pr.val_pr
 ),
 
 y as (SELECT (tek_nalog_na_pribl - otlog_nalog_na_pribl) as nalog_na_pr, id, proch, izm_ot_nalog_ob, izm_ot_nalog_act 
	FROM nalog_na_pribl
	WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
	GROUP BY id, proch, izm_ot_nalog_ob, izm_ot_nalog_act) 
 
 INSERT INTO fin_res_rashchet (id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) 
 SELECT y.id, x.id, x.val_pr, x.pr_ot_prodag, x.prib_do_nalog, y.nalog_na_pr, (x.prib_do_nalog - y.nalog_na_pr - y.izm_ot_nalog_ob - y.izm_ot_nalog_act - y.proch) as chist_pribl
 FROM x,y
 GROUP BY y.id, x.id, x.val_pr, x.pr_ot_prodag, x.prib_do_nalog, y.nalog_na_pr, y.proch, y.izm_ot_nalog_ob, y.izm_ot_nalog_act;
 
return NEW;
END; 
$$;


ALTER FUNCTION public.tr_fin() OWNER TO postgres;

--
-- Name: tr_passiv(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tr_passiv() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

WITH x AS (SELECT SUM(yst_kap + sob_akci + pereocenka_vn_akt + dobav_kap + reserv_kap + neraspred_prib) as itog_kap_res, id
    FROM kap_reserv WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
     GROUP BY id
 ), 
 y as (SELECT SUM(zaymn_sredstva + kredit_zadolg + dohod_bydysh_periodov + ocenoch_ob + proch_ob) as itog_kr_ob, id FROM kratkosr_obzat WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id),
   
  z as (SELECT SUM(zaymn_sredstva + otl_nalog_ob + ocenoch_ob + proch_ob) as itog_dog_ob, id FROM dolgosr_obzat WHERE inn = NEW.inn and id_user = NEW.id_user and year = NEW.year
   GROUP BY id)
 
 
 INSERT INTO balans_passiv (id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) 
 SELECT x.id, y.id, z.id, x.itog_kap_res, y.itog_kr_ob, z.itog_dog_ob, SUM(x.itog_kap_res + y.itog_kr_ob + z.itog_dog_ob) as bal 
 FROM x,y,z
 GROUP BY x.id, y.id, z.id, x.itog_kap_res, y.itog_kr_ob, z.itog_dog_ob;
 
 return NEW;
END; 
$$;


ALTER FUNCTION public.tr_passiv() OWNER TO postgres;

--
-- Name: trigger_ydal_user(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trigger_ydal_user() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	
	if (select count(*) from vhod_v_acc where vhod_v_acc.id_user=OLD.id_user)>0
	then 
		delete from vhod_v_acc where vhod_v_acc.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from ob_aktivs where ob_aktivs.id_user=OLD.id_user)>0
	then 
		if (select count(*) from vn_aktivs where vn_aktivs.id_user=OLD.id_user)>0 then
			if (SELECT count(*) FROM balans_aktiv
				JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
				JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
				WHERE ob_aktivs.id_user = OLD.id_user and vn_aktivs.id_user = OLD.id_user)>0
			then 
				delete from balans_aktiv where id IN (SELECT balans_aktiv.id FROM balans_aktiv
					JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
					JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
					WHERE ob_aktivs.id_user = OLD.id_user and vn_aktivs.id_user = OLD.id_user); 
			end if;
		end if;
		delete from ob_aktivs where ob_aktivs.id_user=OLD.id_user;
		delete from vn_aktivs where vn_aktivs.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from nalog_na_pribl where nalog_na_pribl.id_user=OLD.id_user)>0
	then
		if (select count(*) from fin_res where fin_res.id_user=OLD.id_user)>0
		then 
			if (SELECT count(*) FROM fin_res_rashchet
				JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
				JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
				WHERE nalog_na_pribl.id_user = OLD.id_user and fin_res.id_user = OLD.id_user)>0
			then 
				delete from fin_res_rashchet where id IN (SELECT fin_res_rashchet.id FROM fin_res_rashchet
					JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
					JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
					WHERE nalog_na_pribl.id_user = OLD.id_user and fin_res.id_user = OLD.id_user); 
			end if;
		end if;
		delete from nalog_na_pribl where nalog_na_pribl.id_user=OLD.id_user;
		delete from fin_res where fin_res.id_user=OLD.id_user; 
	end if;
	
	if (select count(*) from dolgosr_obzat where dolgosr_obzat.id_user=OLD.id_user)>0
	then
	
		if (select count(*) from kap_reserv where kap_reserv.id_user=OLD.id_user)>0
		then 
			if (select count(*) from kratkosr_obzat where kratkosr_obzat.id_user=OLD.id_user)>0
			then 
				if (SELECT count(*) FROM balans_passiv
						JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
						JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
						JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
							WHERE dolgosr_obzat.id_user = OLD.id_user
								and kap_reserv.id_user = OLD.id_user
								and kratkosr_obzat.id_user = OLD.id_user)>0
				then 
							delete from balans_passiv where balans_passiv.id IN (SELECT balans_passiv.id FROM balans_passiv
														JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
														JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
														JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
														WHERE dolgosr_obzat.id_user = OLD.id_user
															and kap_reserv.id_user = OLD.id_user
															and kratkosr_obzat.id_user = OLD.id_user); 
				end if;
			end if;
		end if;
		delete from dolgosr_obzat where dolgosr_obzat.id_user=OLD.id_user;
		delete from kap_reserv where kap_reserv.id_user=OLD.id_user; 
		delete from kratkosr_obzat where kratkosr_obzat.id_user=OLD.id_user; 
	end if;
	
	return OLD;

END; 
$$;


ALTER FUNCTION public.trigger_ydal_user() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actions (
    id bigint NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.actions OWNER TO postgres;

--
-- Name: actions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: adm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.adm (
    id_adm bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    password text NOT NULL
);


ALTER TABLE public.adm OWNER TO postgres;

--
-- Name: adm_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.adm_actions (
    id bigint NOT NULL,
    id_ac bigint,
    date date DEFAULT now(),
    "time" time without time zone DEFAULT now(),
    id_adm bigint
);


ALTER TABLE public.adm_actions OWNER TO postgres;

--
-- Name: adm_actions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.adm_actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: adm_id_adm_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.adm ALTER COLUMN id_adm ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_id_adm_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: balans_aktiv; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.balans_aktiv (
    id bigint NOT NULL,
    id_vn_akt bigint,
    id_ob_akt bigint,
    itog_vn numeric NOT NULL,
    itog_ob numeric NOT NULL,
    balans numeric NOT NULL
);


ALTER TABLE public.balans_aktiv OWNER TO postgres;

--
-- Name: balans_aktiv_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.balans_aktiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_aktiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: balans_passiv; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.balans_passiv (
    id bigint NOT NULL,
    id_kap bigint,
    id_krat bigint,
    id_dolg bigint,
    itog_kap numeric NOT NULL,
    itog_krat numeric NOT NULL,
    itog_dolg numeric NOT NULL,
    balans numeric NOT NULL
);


ALTER TABLE public.balans_passiv OWNER TO postgres;

--
-- Name: balans_passiv_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.balans_passiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_passiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dolgosr_obzat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dolgosr_obzat (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zaymn_sredstva numeric NOT NULL,
    otl_nalog_ob numeric NOT NULL,
    ocenoch_ob numeric NOT NULL,
    proch_ob numeric NOT NULL
);


ALTER TABLE public.dolgosr_obzat OWNER TO postgres;

--
-- Name: dolgosr_obzat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.dolgosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.dolgosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fin_res; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fin_res (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    vrychka numeric NOT NULL,
    sebest_prodag numeric NOT NULL,
    kommerchesk_rashod numeric NOT NULL,
    ypravl_rashod numeric NOT NULL,
    dohod_ot_ychast_v_dr_org numeric NOT NULL,
    procent_k_polych numeric NOT NULL,
    procent_k_yplat numeric NOT NULL,
    proch_dohod numeric NOT NULL,
    proch_rashod numeric NOT NULL
);


ALTER TABLE public.fin_res OWNER TO postgres;

--
-- Name: fin_res_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.fin_res ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fin_res_rashchet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fin_res_rashchet (
    id bigint NOT NULL,
    id_nalog_na_pribl bigint,
    id_fin_res bigint,
    val_pr numeric NOT NULL,
    pr_ot_prodag numeric NOT NULL,
    prib_do_nalog numeric NOT NULL,
    nalog_na_pr numeric NOT NULL,
    chist_pribl numeric NOT NULL
);


ALTER TABLE public.fin_res_rashchet OWNER TO postgres;

--
-- Name: fin_res_rashchet_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.fin_res_rashchet ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_rashchet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: kap_reserv; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kap_reserv (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    yst_kap numeric NOT NULL,
    sob_akci numeric NOT NULL,
    pereocenka_vn_akt numeric NOT NULL,
    dobav_kap numeric NOT NULL,
    reserv_kap numeric NOT NULL,
    neraspred_prib numeric NOT NULL
);


ALTER TABLE public.kap_reserv OWNER TO postgres;

--
-- Name: kap_reserv_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.kap_reserv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kap_reserv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: kratkosr_obzat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kratkosr_obzat (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zaymn_sredstva numeric NOT NULL,
    kredit_zadolg numeric NOT NULL,
    dohod_bydysh_periodov numeric NOT NULL,
    ocenoch_ob numeric NOT NULL,
    proch_ob numeric NOT NULL
);


ALTER TABLE public.kratkosr_obzat OWNER TO postgres;

--
-- Name: kratkosr_obzat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.kratkosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kratkosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nalog_na_pribl; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nalog_na_pribl (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    tek_nalog_na_pribl numeric NOT NULL,
    otlog_nalog_na_pribl numeric NOT NULL,
    izm_ot_nalog_ob numeric,
    izm_ot_nalog_act numeric,
    proch numeric
);


ALTER TABLE public.nalog_na_pribl OWNER TO postgres;

--
-- Name: nalog_na_pribl_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.nalog_na_pribl ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.nalog_na_pribl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ob_aktivs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ob_aktivs (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    zapas numeric NOT NULL,
    nalog_na_dob_st_po_pr_cen numeric NOT NULL,
    debitor_zadolg numeric NOT NULL,
    finans_vlog numeric NOT NULL,
    proch_obor_aktiv numeric NOT NULL,
    deneg_sredstv numeric NOT NULL
);


ALTER TABLE public.ob_aktivs OWNER TO postgres;

--
-- Name: ob_aktivs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.ob_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ob_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id_user bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    phone character varying(20) NOT NULL,
    password text NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_user_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.users ALTER COLUMN id_user ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vhod_v_acc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vhod_v_acc (
    id_vhod bigint NOT NULL,
    date_vhod date DEFAULT now(),
    time_vhod time without time zone DEFAULT now(),
    id_user bigint
);


ALTER TABLE public.vhod_v_acc OWNER TO postgres;

--
-- Name: vhod_v_acc_id_vhod_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.vhod_v_acc ALTER COLUMN id_vhod ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vhod_v_acc_id_vhod_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vn_aktivs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vn_aktivs (
    id bigint NOT NULL,
    inn character varying(50) NOT NULL,
    id_user bigint,
    year date NOT NULL,
    nemater_akt numeric NOT NULL,
    res_issl_rasrab numeric NOT NULL,
    nemater_poisk_akt numeric NOT NULL,
    mater_poisk_akt numeric NOT NULL,
    ostov_sredstva numeric NOT NULL,
    dohod_vlog_v_mat numeric NOT NULL,
    fin_vlog numeric NOT NULL,
    otlog_nalog_aktiv numeric NOT NULL,
    proch_vneob_akt numeric NOT NULL,
    avans_na_kap_str numeric NOT NULL,
    nezav_str numeric NOT NULL
);


ALTER TABLE public.vn_aktivs OWNER TO postgres;

--
-- Name: vn_aktivs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.vn_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vn_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actions (id, name) FROM stdin;
\.
COPY public.actions (id, name) FROM '$$PATH$$/3717.dat';

--
-- Data for Name: adm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.adm (id_adm, name, login, email, password) FROM stdin;
\.
COPY public.adm (id_adm, name, login, email, password) FROM '$$PATH$$/3715.dat';

--
-- Data for Name: adm_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.adm_actions (id, id_ac, date, "time", id_adm) FROM stdin;
\.
COPY public.adm_actions (id, id_ac, date, "time", id_adm) FROM '$$PATH$$/3719.dat';

--
-- Data for Name: balans_aktiv; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.balans_aktiv (id, id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) FROM stdin;
\.
COPY public.balans_aktiv (id, id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) FROM '$$PATH$$/3725.dat';

--
-- Data for Name: balans_passiv; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.balans_passiv (id, id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) FROM stdin;
\.
COPY public.balans_passiv (id, id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) FROM '$$PATH$$/3733.dat';

--
-- Data for Name: dolgosr_obzat; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dolgosr_obzat (id, inn, id_user, year, zaymn_sredstva, otl_nalog_ob, ocenoch_ob, proch_ob) FROM stdin;
\.
COPY public.dolgosr_obzat (id, inn, id_user, year, zaymn_sredstva, otl_nalog_ob, ocenoch_ob, proch_ob) FROM '$$PATH$$/3731.dat';

--
-- Data for Name: fin_res; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fin_res (id, inn, id_user, year, vrychka, sebest_prodag, kommerchesk_rashod, ypravl_rashod, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, proch_rashod) FROM stdin;
\.
COPY public.fin_res (id, inn, id_user, year, vrychka, sebest_prodag, kommerchesk_rashod, ypravl_rashod, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, proch_rashod) FROM '$$PATH$$/3737.dat';

--
-- Data for Name: fin_res_rashchet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fin_res_rashchet (id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) FROM stdin;
\.
COPY public.fin_res_rashchet (id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) FROM '$$PATH$$/3739.dat';

--
-- Data for Name: kap_reserv; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kap_reserv (id, inn, id_user, year, yst_kap, sob_akci, pereocenka_vn_akt, dobav_kap, reserv_kap, neraspred_prib) FROM stdin;
\.
COPY public.kap_reserv (id, inn, id_user, year, yst_kap, sob_akci, pereocenka_vn_akt, dobav_kap, reserv_kap, neraspred_prib) FROM '$$PATH$$/3727.dat';

--
-- Data for Name: kratkosr_obzat; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kratkosr_obzat (id, inn, id_user, year, zaymn_sredstva, kredit_zadolg, dohod_bydysh_periodov, ocenoch_ob, proch_ob) FROM stdin;
\.
COPY public.kratkosr_obzat (id, inn, id_user, year, zaymn_sredstva, kredit_zadolg, dohod_bydysh_periodov, ocenoch_ob, proch_ob) FROM '$$PATH$$/3729.dat';

--
-- Data for Name: nalog_na_pribl; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nalog_na_pribl (id, inn, id_user, year, tek_nalog_na_pribl, otlog_nalog_na_pribl, izm_ot_nalog_ob, izm_ot_nalog_act, proch) FROM stdin;
\.
COPY public.nalog_na_pribl (id, inn, id_user, year, tek_nalog_na_pribl, otlog_nalog_na_pribl, izm_ot_nalog_ob, izm_ot_nalog_act, proch) FROM '$$PATH$$/3735.dat';

--
-- Data for Name: ob_aktivs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ob_aktivs (id, inn, id_user, year, zapas, nalog_na_dob_st_po_pr_cen, debitor_zadolg, finans_vlog, proch_obor_aktiv, deneg_sredstv) FROM stdin;
\.
COPY public.ob_aktivs (id, inn, id_user, year, zapas, nalog_na_dob_st_po_pr_cen, debitor_zadolg, finans_vlog, proch_obor_aktiv, deneg_sredstv) FROM '$$PATH$$/3723.dat';

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id_user, name, login, email, phone, password) FROM stdin;
\.
COPY public.users (id_user, name, login, email, phone, password) FROM '$$PATH$$/3711.dat';

--
-- Data for Name: vhod_v_acc; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vhod_v_acc (id_vhod, date_vhod, time_vhod, id_user) FROM stdin;
\.
COPY public.vhod_v_acc (id_vhod, date_vhod, time_vhod, id_user) FROM '$$PATH$$/3713.dat';

--
-- Data for Name: vn_aktivs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vn_aktivs (id, inn, id_user, year, nemater_akt, res_issl_rasrab, nemater_poisk_akt, mater_poisk_akt, ostov_sredstva, dohod_vlog_v_mat, fin_vlog, otlog_nalog_aktiv, proch_vneob_akt, avans_na_kap_str, nezav_str) FROM stdin;
\.
COPY public.vn_aktivs (id, inn, id_user, year, nemater_akt, res_issl_rasrab, nemater_poisk_akt, mater_poisk_akt, ostov_sredstva, dohod_vlog_v_mat, fin_vlog, otlog_nalog_aktiv, proch_vneob_akt, avans_na_kap_str, nezav_str) FROM '$$PATH$$/3721.dat';

--
-- Name: actions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actions_id_seq', 3, true);


--
-- Name: adm_actions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.adm_actions_id_seq', 5, true);


--
-- Name: adm_id_adm_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.adm_id_adm_seq', 2, true);


--
-- Name: balans_aktiv_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.balans_aktiv_id_seq', 22, true);


--
-- Name: balans_passiv_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.balans_passiv_id_seq', 13, true);


--
-- Name: dolgosr_obzat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dolgosr_obzat_id_seq', 14, true);


--
-- Name: fin_res_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fin_res_id_seq', 15, true);


--
-- Name: fin_res_rashchet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fin_res_rashchet_id_seq', 13, true);


--
-- Name: kap_reserv_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kap_reserv_id_seq', 15, true);


--
-- Name: kratkosr_obzat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kratkosr_obzat_id_seq', 14, true);


--
-- Name: nalog_na_pribl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nalog_na_pribl_id_seq', 15, true);


--
-- Name: ob_aktivs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ob_aktivs_id_seq', 23, true);


--
-- Name: users_id_user_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_user_seq', 5, true);


--
-- Name: vhod_v_acc_id_vhod_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vhod_v_acc_id_vhod_seq', 59, true);


--
-- Name: vn_aktivs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vn_aktivs_id_seq', 23, true);


--
-- Name: actions actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_pkey PRIMARY KEY (id);


--
-- Name: adm_actions adm_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_pkey PRIMARY KEY (id);


--
-- Name: adm adm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.adm
    ADD CONSTRAINT adm_pkey PRIMARY KEY (id_adm);


--
-- Name: balans_aktiv balans_aktiv_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_pkey PRIMARY KEY (id);


--
-- Name: balans_passiv balans_passiv_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_pkey PRIMARY KEY (id);


--
-- Name: dolgosr_obzat dolgosr_obzat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_pkey PRIMARY KEY (id);


--
-- Name: fin_res fin_res_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_pkey PRIMARY KEY (id);


--
-- Name: fin_res_rashchet fin_res_rashchet_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_pkey PRIMARY KEY (id);


--
-- Name: kap_reserv kap_reserv_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_pkey PRIMARY KEY (id);


--
-- Name: kratkosr_obzat kratkosr_obzat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_pkey PRIMARY KEY (id);


--
-- Name: nalog_na_pribl nalog_na_pribl_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_pkey PRIMARY KEY (id);


--
-- Name: ob_aktivs ob_aktivs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);


--
-- Name: vhod_v_acc vhod_v_acc_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_pkey PRIMARY KEY (id_vhod);


--
-- Name: vn_aktivs vn_aktivs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_pkey PRIMARY KEY (id);


--
-- Name: ob_aktivs tr_aktiv; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_aktiv AFTER INSERT ON public.ob_aktivs FOR EACH ROW EXECUTE FUNCTION public.tr_aktiv();


--
-- Name: nalog_na_pribl tr_fin; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_fin AFTER INSERT ON public.nalog_na_pribl FOR EACH ROW EXECUTE FUNCTION public.tr_fin();


--
-- Name: kratkosr_obzat tr_passiv; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_passiv AFTER INSERT ON public.kratkosr_obzat FOR EACH ROW EXECUTE FUNCTION public.tr_passiv();


--
-- Name: users trigger_ydal_user; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_ydal_user BEFORE DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trigger_ydal_user();


--
-- Name: adm_actions adm_actions_id_ac_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_ac_fkey FOREIGN KEY (id_ac) REFERENCES public.actions(id);


--
-- Name: adm_actions adm_actions_id_adm_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_adm_fkey FOREIGN KEY (id_adm) REFERENCES public.adm(id_adm);


--
-- Name: balans_aktiv balans_aktiv_id_ob_akt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_ob_akt_fkey FOREIGN KEY (id_ob_akt) REFERENCES public.ob_aktivs(id);


--
-- Name: balans_aktiv balans_aktiv_id_vn_akt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_vn_akt_fkey FOREIGN KEY (id_vn_akt) REFERENCES public.vn_aktivs(id);


--
-- Name: balans_passiv balans_passiv_id_dolg_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_dolg_fkey FOREIGN KEY (id_dolg) REFERENCES public.dolgosr_obzat(id);


--
-- Name: balans_passiv balans_passiv_id_kap_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_kap_fkey FOREIGN KEY (id_kap) REFERENCES public.kap_reserv(id);


--
-- Name: balans_passiv balans_passiv_id_krat_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_krat_fkey FOREIGN KEY (id_krat) REFERENCES public.kratkosr_obzat(id);


--
-- Name: dolgosr_obzat dolgosr_obzat_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: fin_res fin_res_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: fin_res_rashchet fin_res_rashchet_id_fin_res_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_fin_res_fkey FOREIGN KEY (id_fin_res) REFERENCES public.fin_res(id);


--
-- Name: fin_res_rashchet fin_res_rashchet_id_nalog_na_pribl_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_nalog_na_pribl_fkey FOREIGN KEY (id_nalog_na_pribl) REFERENCES public.nalog_na_pribl(id);


--
-- Name: kap_reserv kap_reserv_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: kratkosr_obzat kratkosr_obzat_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: nalog_na_pribl nalog_na_pribl_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: ob_aktivs ob_aktivs_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: vhod_v_acc vhod_v_acc_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- Name: vn_aktivs vn_aktivs_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);


--
-- PostgreSQL database dump complete
--

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      