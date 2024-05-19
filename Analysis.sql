PGDMP     ;    %                 |            Analiz    15.2    15.2 h    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    35987    Analiz    DATABASE     j   CREATE DATABASE "Analiz" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';
    DROP DATABASE "Analiz";
                postgres    false            �            1255    36348 
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
       public          postgres    false                       1255    36356    tr_fin()    FUNCTION     �  CREATE FUNCTION public.tr_fin() RETURNS trigger
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
       public          postgres    false                        1255    36353    tr_passiv()    FUNCTION     5  CREATE FUNCTION public.tr_passiv() RETURNS trigger
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
       public          postgres    false                       1255    36796    trigger_ydal_user()    FUNCTION     �  CREATE FUNCTION public.trigger_ydal_user() RETURNS trigger
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
       public          postgres    false            �            1259    36055    actions    TABLE     P   CREATE TABLE public.actions (
    id bigint NOT NULL,
    name text NOT NULL
);
    DROP TABLE public.actions;
       public         heap    postgres    false            �            1259    36054    actions_id_seq    SEQUENCE     �   ALTER TABLE public.actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    221            �            1259    36047    adm    TABLE     �   CREATE TABLE public.adm (
    id_adm bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    password text NOT NULL
);
    DROP TABLE public.adm;
       public         heap    postgres    false            �            1259    36063    adm_actions    TABLE     �   CREATE TABLE public.adm_actions (
    id bigint NOT NULL,
    id_ac bigint,
    date date DEFAULT now(),
    "time" time without time zone DEFAULT now(),
    id_adm bigint
);
    DROP TABLE public.adm_actions;
       public         heap    postgres    false            �            1259    36062    adm_actions_id_seq    SEQUENCE     �   ALTER TABLE public.adm_actions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    223            �            1259    36046    adm_id_adm_seq    SEQUENCE     �   ALTER TABLE public.adm ALTER COLUMN id_adm ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adm_id_adm_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    219            �            1259    36223    balans_aktiv    TABLE     �   CREATE TABLE public.balans_aktiv (
    id bigint NOT NULL,
    id_vn_akt bigint,
    id_ob_akt bigint,
    itog_vn numeric NOT NULL,
    itog_ob numeric NOT NULL,
    balans numeric NOT NULL
);
     DROP TABLE public.balans_aktiv;
       public         heap    postgres    false            �            1259    36222    balans_aktiv_id_seq    SEQUENCE     �   ALTER TABLE public.balans_aktiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_aktiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    229            �            1259    36281    balans_passiv    TABLE     �   CREATE TABLE public.balans_passiv (
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
       public         heap    postgres    false            �            1259    36280    balans_passiv_id_seq    SEQUENCE     �   ALTER TABLE public.balans_passiv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.balans_passiv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    237            �            1259    36268    dolgosr_obzat    TABLE       CREATE TABLE public.dolgosr_obzat (
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
       public         heap    postgres    false            �            1259    36267    dolgosr_obzat_id_seq    SEQUENCE     �   ALTER TABLE public.dolgosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.dolgosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    235            �            1259    36317    fin_res    TABLE     �  CREATE TABLE public.fin_res (
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
       public         heap    postgres    false            �            1259    36316    fin_res_id_seq    SEQUENCE     �   ALTER TABLE public.fin_res ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    241            �            1259    36330    fin_res_rashchet    TABLE       CREATE TABLE public.fin_res_rashchet (
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
       public         heap    postgres    false            �            1259    36329    fin_res_rashchet_id_seq    SEQUENCE     �   ALTER TABLE public.fin_res_rashchet ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fin_res_rashchet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    243            �            1259    36242 
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
       public         heap    postgres    false            �            1259    36241    kap_reserv_id_seq    SEQUENCE     �   ALTER TABLE public.kap_reserv ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kap_reserv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    231            �            1259    36255    kratkosr_obzat    TABLE     H  CREATE TABLE public.kratkosr_obzat (
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
       public         heap    postgres    false            �            1259    36254    kratkosr_obzat_id_seq    SEQUENCE     �   ALTER TABLE public.kratkosr_obzat ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.kratkosr_obzat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    233            �            1259    36304    nalog_na_pribl    TABLE     5  CREATE TABLE public.nalog_na_pribl (
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
       public         heap    postgres    false            �            1259    36303    nalog_na_pribl_id_seq    SEQUENCE     �   ALTER TABLE public.nalog_na_pribl ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.nalog_na_pribl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    239            �            1259    36210 	   ob_aktivs    TABLE     l  CREATE TABLE public.ob_aktivs (
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
       public         heap    postgres    false            �            1259    36209    ob_aktivs_id_seq    SEQUENCE     �   ALTER TABLE public.ob_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ob_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    227            �            1259    36026    users    TABLE     �   CREATE TABLE public.users (
    id_user bigint NOT NULL,
    name character varying(50) NOT NULL,
    login character varying(50) NOT NULL,
    email text NOT NULL,
    phone character varying(20) NOT NULL,
    password text NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    36025    users_id_user_seq    SEQUENCE     �   ALTER TABLE public.users ALTER COLUMN id_user ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    215            �            1259    36034 
   vhod_v_acc    TABLE     �   CREATE TABLE public.vhod_v_acc (
    id_vhod bigint NOT NULL,
    date_vhod date DEFAULT now(),
    time_vhod time without time zone DEFAULT now(),
    id_user bigint
);
    DROP TABLE public.vhod_v_acc;
       public         heap    postgres    false            �            1259    36033    vhod_v_acc_id_vhod_seq    SEQUENCE     �   ALTER TABLE public.vhod_v_acc ALTER COLUMN id_vhod ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vhod_v_acc_id_vhod_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    217            �            1259    36197 	   vn_aktivs    TABLE     $  CREATE TABLE public.vn_aktivs (
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
       public         heap    postgres    false            �            1259    36196    vn_aktivs_id_seq    SEQUENCE     �   ALTER TABLE public.vn_aktivs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.vn_aktivs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    225            �          0    36055    actions 
   TABLE DATA           +   COPY public.actions (id, name) FROM stdin;
    public          postgres    false    221   v�       �          0    36047    adm 
   TABLE DATA           C   COPY public.adm (id_adm, name, login, email, password) FROM stdin;
    public          postgres    false    219   �       �          0    36063    adm_actions 
   TABLE DATA           F   COPY public.adm_actions (id, id_ac, date, "time", id_adm) FROM stdin;
    public          postgres    false    223   ��       �          0    36223    balans_aktiv 
   TABLE DATA           Z   COPY public.balans_aktiv (id, id_vn_akt, id_ob_akt, itog_vn, itog_ob, balans) FROM stdin;
    public          postgres    false    229   �       �          0    36281    balans_passiv 
   TABLE DATA           m   COPY public.balans_passiv (id, id_kap, id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans) FROM stdin;
    public          postgres    false    237   ��       �          0    36268    dolgosr_obzat 
   TABLE DATA           s   COPY public.dolgosr_obzat (id, inn, id_user, year, zaymn_sredstva, otl_nalog_ob, ocenoch_ob, proch_ob) FROM stdin;
    public          postgres    false    235   X�       �          0    36317    fin_res 
   TABLE DATA           �   COPY public.fin_res (id, inn, id_user, year, vrychka, sebest_prodag, kommerchesk_rashod, ypravl_rashod, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, proch_rashod) FROM stdin;
    public          postgres    false    241   �       �          0    36330    fin_res_rashchet 
   TABLE DATA           �   COPY public.fin_res_rashchet (id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl) FROM stdin;
    public          postgres    false    243   �       �          0    36242 
   kap_reserv 
   TABLE DATA           �   COPY public.kap_reserv (id, inn, id_user, year, yst_kap, sob_akci, pereocenka_vn_akt, dobav_kap, reserv_kap, neraspred_prib) FROM stdin;
    public          postgres    false    231   ��       �          0    36255    kratkosr_obzat 
   TABLE DATA           �   COPY public.kratkosr_obzat (id, inn, id_user, year, zaymn_sredstva, kredit_zadolg, dohod_bydysh_periodov, ocenoch_ob, proch_ob) FROM stdin;
    public          postgres    false    233   C�       �          0    36304    nalog_na_pribl 
   TABLE DATA           �   COPY public.nalog_na_pribl (id, inn, id_user, year, tek_nalog_na_pribl, otlog_nalog_na_pribl, izm_ot_nalog_ob, izm_ot_nalog_act, proch) FROM stdin;
    public          postgres    false    239   ��       �          0    36210 	   ob_aktivs 
   TABLE DATA           �   COPY public.ob_aktivs (id, inn, id_user, year, zapas, nalog_na_dob_st_po_pr_cen, debitor_zadolg, finans_vlog, proch_obor_aktiv, deneg_sredstv) FROM stdin;
    public          postgres    false    227   ��                 0    36026    users 
   TABLE DATA           M   COPY public.users (id_user, name, login, email, phone, password) FROM stdin;
    public          postgres    false    215   o�       �          0    36034 
   vhod_v_acc 
   TABLE DATA           L   COPY public.vhod_v_acc (id_vhod, date_vhod, time_vhod, id_user) FROM stdin;
    public          postgres    false    217   ��       �          0    36197 	   vn_aktivs 
   TABLE DATA           �   COPY public.vn_aktivs (id, inn, id_user, year, nemater_akt, res_issl_rasrab, nemater_poisk_akt, mater_poisk_akt, ostov_sredstva, dohod_vlog_v_mat, fin_vlog, otlog_nalog_aktiv, proch_vneob_akt, avans_na_kap_str, nezav_str) FROM stdin;
    public          postgres    false    225   w�       �           0    0    actions_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.actions_id_seq', 3, true);
          public          postgres    false    220            �           0    0    adm_actions_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.adm_actions_id_seq', 5, true);
          public          postgres    false    222            �           0    0    adm_id_adm_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.adm_id_adm_seq', 2, true);
          public          postgres    false    218            �           0    0    balans_aktiv_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.balans_aktiv_id_seq', 22, true);
          public          postgres    false    228            �           0    0    balans_passiv_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.balans_passiv_id_seq', 13, true);
          public          postgres    false    236            �           0    0    dolgosr_obzat_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.dolgosr_obzat_id_seq', 14, true);
          public          postgres    false    234            �           0    0    fin_res_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.fin_res_id_seq', 15, true);
          public          postgres    false    240            �           0    0    fin_res_rashchet_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.fin_res_rashchet_id_seq', 13, true);
          public          postgres    false    242            �           0    0    kap_reserv_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.kap_reserv_id_seq', 15, true);
          public          postgres    false    230            �           0    0    kratkosr_obzat_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.kratkosr_obzat_id_seq', 14, true);
          public          postgres    false    232            �           0    0    nalog_na_pribl_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.nalog_na_pribl_id_seq', 15, true);
          public          postgres    false    238            �           0    0    ob_aktivs_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.ob_aktivs_id_seq', 23, true);
          public          postgres    false    226            �           0    0    users_id_user_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.users_id_user_seq', 5, true);
          public          postgres    false    214            �           0    0    vhod_v_acc_id_vhod_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.vhod_v_acc_id_vhod_seq', 59, true);
          public          postgres    false    216            �           0    0    vn_aktivs_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.vn_aktivs_id_seq', 23, true);
          public          postgres    false    224            �           2606    36061    actions actions_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.actions DROP CONSTRAINT actions_pkey;
       public            postgres    false    221            �           2606    36069    adm_actions adm_actions_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_pkey;
       public            postgres    false    223            �           2606    36053    adm adm_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.adm
    ADD CONSTRAINT adm_pkey PRIMARY KEY (id_adm);
 6   ALTER TABLE ONLY public.adm DROP CONSTRAINT adm_pkey;
       public            postgres    false    219            �           2606    36229    balans_aktiv balans_aktiv_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_pkey;
       public            postgres    false    229            �           2606    36287     balans_passiv balans_passiv_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_pkey;
       public            postgres    false    237            �           2606    36274     dolgosr_obzat dolgosr_obzat_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.dolgosr_obzat DROP CONSTRAINT dolgosr_obzat_pkey;
       public            postgres    false    235            �           2606    36323    fin_res fin_res_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.fin_res DROP CONSTRAINT fin_res_pkey;
       public            postgres    false    241            �           2606    36336 &   fin_res_rashchet fin_res_rashchet_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_pkey;
       public            postgres    false    243            �           2606    36248    kap_reserv kap_reserv_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.kap_reserv DROP CONSTRAINT kap_reserv_pkey;
       public            postgres    false    231            �           2606    36261 "   kratkosr_obzat kratkosr_obzat_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.kratkosr_obzat DROP CONSTRAINT kratkosr_obzat_pkey;
       public            postgres    false    233            �           2606    36310 "   nalog_na_pribl nalog_na_pribl_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.nalog_na_pribl DROP CONSTRAINT nalog_na_pribl_pkey;
       public            postgres    false    239            �           2606    36216    ob_aktivs ob_aktivs_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.ob_aktivs DROP CONSTRAINT ob_aktivs_pkey;
       public            postgres    false    227            �           2606    36032    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    215            �           2606    36040    vhod_v_acc vhod_v_acc_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_pkey PRIMARY KEY (id_vhod);
 D   ALTER TABLE ONLY public.vhod_v_acc DROP CONSTRAINT vhod_v_acc_pkey;
       public            postgres    false    217            �           2606    36203    vn_aktivs vn_aktivs_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.vn_aktivs DROP CONSTRAINT vn_aktivs_pkey;
       public            postgres    false    225            �           2620    36352    ob_aktivs tr_aktiv    TRIGGER     j   CREATE TRIGGER tr_aktiv AFTER INSERT ON public.ob_aktivs FOR EACH ROW EXECUTE FUNCTION public.tr_aktiv();
 +   DROP TRIGGER tr_aktiv ON public.ob_aktivs;
       public          postgres    false    255    227            �           2620    36795    nalog_na_pribl tr_fin    TRIGGER     k   CREATE TRIGGER tr_fin AFTER INSERT ON public.nalog_na_pribl FOR EACH ROW EXECUTE FUNCTION public.tr_fin();
 .   DROP TRIGGER tr_fin ON public.nalog_na_pribl;
       public          postgres    false    258    239            �           2620    36354    kratkosr_obzat tr_passiv    TRIGGER     q   CREATE TRIGGER tr_passiv AFTER INSERT ON public.kratkosr_obzat FOR EACH ROW EXECUTE FUNCTION public.tr_passiv();
 1   DROP TRIGGER tr_passiv ON public.kratkosr_obzat;
       public          postgres    false    256    233            �           2620    36800    users trigger_ydal_user    TRIGGER     y   CREATE TRIGGER trigger_ydal_user BEFORE DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trigger_ydal_user();
 0   DROP TRIGGER trigger_ydal_user ON public.users;
       public          postgres    false    215    257            �           2606    36070 "   adm_actions adm_actions_id_ac_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_ac_fkey FOREIGN KEY (id_ac) REFERENCES public.actions(id);
 L   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_id_ac_fkey;
       public          postgres    false    223    221    3524            �           2606    36075 #   adm_actions adm_actions_id_adm_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.adm_actions
    ADD CONSTRAINT adm_actions_id_adm_fkey FOREIGN KEY (id_adm) REFERENCES public.adm(id_adm);
 M   ALTER TABLE ONLY public.adm_actions DROP CONSTRAINT adm_actions_id_adm_fkey;
       public          postgres    false    219    3522    223            �           2606    36235 (   balans_aktiv balans_aktiv_id_ob_akt_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_ob_akt_fkey FOREIGN KEY (id_ob_akt) REFERENCES public.ob_aktivs(id);
 R   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_id_ob_akt_fkey;
       public          postgres    false    229    227    3530            �           2606    36230 (   balans_aktiv balans_aktiv_id_vn_akt_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_aktiv
    ADD CONSTRAINT balans_aktiv_id_vn_akt_fkey FOREIGN KEY (id_vn_akt) REFERENCES public.vn_aktivs(id);
 R   ALTER TABLE ONLY public.balans_aktiv DROP CONSTRAINT balans_aktiv_id_vn_akt_fkey;
       public          postgres    false    225    229    3528            �           2606    36298 (   balans_passiv balans_passiv_id_dolg_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_dolg_fkey FOREIGN KEY (id_dolg) REFERENCES public.dolgosr_obzat(id);
 R   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_dolg_fkey;
       public          postgres    false    237    3538    235            �           2606    36288 '   balans_passiv balans_passiv_id_kap_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_kap_fkey FOREIGN KEY (id_kap) REFERENCES public.kap_reserv(id);
 Q   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_kap_fkey;
       public          postgres    false    3534    237    231            �           2606    36293 (   balans_passiv balans_passiv_id_krat_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.balans_passiv
    ADD CONSTRAINT balans_passiv_id_krat_fkey FOREIGN KEY (id_krat) REFERENCES public.kratkosr_obzat(id);
 R   ALTER TABLE ONLY public.balans_passiv DROP CONSTRAINT balans_passiv_id_krat_fkey;
       public          postgres    false    233    237    3536            �           2606    36275 (   dolgosr_obzat dolgosr_obzat_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.dolgosr_obzat
    ADD CONSTRAINT dolgosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 R   ALTER TABLE ONLY public.dolgosr_obzat DROP CONSTRAINT dolgosr_obzat_id_user_fkey;
       public          postgres    false    215    3518    235            �           2606    36324    fin_res fin_res_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res
    ADD CONSTRAINT fin_res_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 F   ALTER TABLE ONLY public.fin_res DROP CONSTRAINT fin_res_id_user_fkey;
       public          postgres    false    241    215    3518            �           2606    36342 1   fin_res_rashchet fin_res_rashchet_id_fin_res_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_fin_res_fkey FOREIGN KEY (id_fin_res) REFERENCES public.fin_res(id);
 [   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_id_fin_res_fkey;
       public          postgres    false    243    3544    241            �           2606    36337 8   fin_res_rashchet fin_res_rashchet_id_nalog_na_pribl_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fin_res_rashchet
    ADD CONSTRAINT fin_res_rashchet_id_nalog_na_pribl_fkey FOREIGN KEY (id_nalog_na_pribl) REFERENCES public.nalog_na_pribl(id);
 b   ALTER TABLE ONLY public.fin_res_rashchet DROP CONSTRAINT fin_res_rashchet_id_nalog_na_pribl_fkey;
       public          postgres    false    243    3542    239            �           2606    36249 "   kap_reserv kap_reserv_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.kap_reserv
    ADD CONSTRAINT kap_reserv_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 L   ALTER TABLE ONLY public.kap_reserv DROP CONSTRAINT kap_reserv_id_user_fkey;
       public          postgres    false    215    231    3518            �           2606    36262 *   kratkosr_obzat kratkosr_obzat_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.kratkosr_obzat
    ADD CONSTRAINT kratkosr_obzat_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 T   ALTER TABLE ONLY public.kratkosr_obzat DROP CONSTRAINT kratkosr_obzat_id_user_fkey;
       public          postgres    false    233    215    3518            �           2606    36311 *   nalog_na_pribl nalog_na_pribl_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.nalog_na_pribl
    ADD CONSTRAINT nalog_na_pribl_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 T   ALTER TABLE ONLY public.nalog_na_pribl DROP CONSTRAINT nalog_na_pribl_id_user_fkey;
       public          postgres    false    215    3518    239            �           2606    36217     ob_aktivs ob_aktivs_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.ob_aktivs
    ADD CONSTRAINT ob_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 J   ALTER TABLE ONLY public.ob_aktivs DROP CONSTRAINT ob_aktivs_id_user_fkey;
       public          postgres    false    3518    215    227            �           2606    36041 "   vhod_v_acc vhod_v_acc_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.vhod_v_acc
    ADD CONSTRAINT vhod_v_acc_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 L   ALTER TABLE ONLY public.vhod_v_acc DROP CONSTRAINT vhod_v_acc_id_user_fkey;
       public          postgres    false    215    217    3518            �           2606    36204     vn_aktivs vn_aktivs_id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.vn_aktivs
    ADD CONSTRAINT vn_aktivs_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id_user);
 J   ALTER TABLE ONLY public.vn_aktivs DROP CONSTRAINT vn_aktivs_id_user_fkey;
       public          postgres    false    3518    215    225            �   f   x�]��	�0���U�A��1� ��@����·��z���Վ�/�D��&sx3w�Y�jF��9MQ�EE'�8f�O�Q{n�V"���L�      �   �   x�E�;�0k��#{6�;PѬ�XD��Ap
J��%��G©���i4��Gz�g�2jzɺ��|f=u��xfr�K����g� ����4�Ӛ@�ڈ��]�s�ðo��C��i���6zj���*�Dp��HZa�����*�T
�W$@��W%���d7�      �   Z   x�mα�@�zo�P���çTv<?�%�B^��{�4�\����	N��X� '�U��$���1ty? �@Y#��m�����      �   �   x���@�PL�\���:�F�ٜN��C`c��m+Ӎ���IԒ�pF0� ��L+Ʈ�F[��9��*�Ɯ���>�oO��lGd�p���>��Y	�ғ�sϚ��dE�`�n���#��y����l�����?�C*|      �   �   x���@B�l1�/鿎���đ��0̣[�$�b����d�D�N��V�L3��1]MA^���<�F�.�bL^²�.���M��\y_QML��8��0�U&	ņ�G���܆#}x��-�s��ƣ��vLM�e�坨n���;�씣�l��T�l���y�� @139      �   �   x�e��0Dѳ�h�Kl�B�u� !r���d���I�(���(�J/��RS ��8<��L�����<�9��
�b���Y��y�:�D�Hw��Θ���:ש���Ƴ����=��z�3ʶ�J� .j��%
۪���z�1�R6�      �     x�e�ɍ0�r/Y�����_G� �$/�=<Fz���@LM��C������d
;:�b�6i����!���!�V�<g�1؜�*υY�
��K�%Ն=�pɱrw��\����~[`>L�Yܠn�6P��SD����*�NfCB� ?����*�n�@���I����,�*6���Z73�$�]y`�[Ag�w{�	�nΊ	������t*��:N����7gʦ8��߼
'�/�&s���������9�	�$^9      �   �   x�-O�qP:k1����:�����Q,�+�ҹN�0S�5�n/A�;ڲW`u&,���cVlE�TO�xzZO�>@w�jk����ݼm��%,��z��ǚ��~�f�ꉬ�� e.I�������7`M���S�C��{�l\����}��Q�?.1O      �   �   x����A㣗�X�`����a��l-�!�*"���25\��g�Ba/� ,��,cQ�0��iژ�����f�E�v�a�i�����aY&=�%�����O]�8�e2�;l'�[��	o6���!"//�>F      �   �   x�e���0�o�K+�t�9J�D��?d��e7bjx�>#B���vv��x3#Zt�����Ո�DѠ�qԌJ�}�,ҼR�;�qF-�Lk�\]9�D��Dx�Aie=�W����.��/}N`��ѵ��7`'��F�<��O��
��E*9-ʔC�����s���mA)      �      x�e��QC�u^/ ;������Ͱ`��=�۪������!Z�;�փ�ð/U��fxWB0)��/�"��D(�vV�`���ѱ!opN���6���G�{O��)�g��=�F�H���\k�/Q      �   �   x�e�KnD1��.���K����)�[�PRz���@L/��!i���k-��QKQ����Ȋt;���[���oi���11�X�ֲ�5I��/�~$�� ҙ��vբ%w���kt���X�f�Ah�r�m����Ճ�
J/#����o�^�ب��7�`�}Xv�lp3����V����7ʽ�efUg̻l�mZ��s���O�         9  x�m�MJCA��{�x��L2��LW� V�*.�M��V�-m�'���;�H��Rh��#Pm?�_���w�Ϋ5TӍ�d��[>W��@��x�]0]�"<����D���jWM|7�WSX���+�� �O�#f\P:g��H%���|!#����l�U���Uǥ��2��� ܁���&���f��M���p�2x[	O��PiQ��8�S���1X`�YY!�.�+ڗ(��X�FG�ZW�Y������Pwlk��E���|}2:�p�M�ϨQ"�Hb�Ta�>�b2i��!eT�U.:�1�b���`Q��\������~�      �   �  x�m�Yr�0C�����;)�e���L�d>�^����0x"�s1����������qP��B�"Z*ÓY��Xx�\�O���e�8�Py��qa>h.��y�JfO��(�X��H����m���!\����|���f�8~�[ƨa�9���|�������%<�-gǗrJ��\�?���?��CvƏ�1܃�6�wεH��t�ޞ����e:Jͨ��|pǣB!�GѼ<�������������ʽ�����~q�����r����IF���Vϰ������N!����V��M]*���y��\8i�>��l[]�/8k�¹4��_w���uL`ݪ�P�o����Ty�Is�;�d��i���/n;Xh1�0��c)���d�F��^|�.E�G�k�W��yt�!q"��������{"d�w�u5�M�}4/�Ӂ$�.gڼ~8����~?\�j�O�>۽�ӌl�9��^n�G��]��� �k�7��v釠�����������q�oXQ����H��iky�9m��/W�.��v�k_�!U����x�����V�9䏰���&_�H�����uzp���H	�=�t~phom�o{��x��#3ˡ������v�����q@
�e���o������q�������}Q���������׳��q��_�4D�      �   �   x�e��m�@�3Ջ���K��#�,#q]X�#�DH5�^�x����R���pkTm���r���2	��_uG}hzk�W�4so����,Cu�҉= ��KX9��cn��_�2�}s��K2���\#Je���^�����_#��^�3��g3){'駼�<��0�=ib�m�-ߓy�;�<=��,� o�\mۄ�Z��3wd;ލ�0�e��w��˽��v!|C�����Wx[%     