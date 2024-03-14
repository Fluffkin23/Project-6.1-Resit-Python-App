--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-10-04 11:59:04

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
-- TOC entry 223 (class 1255 OID 58049)
-- Name: delete_member(integer); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.delete_member(IN memberid integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM Member WHERE Member.memberID = delete_member.memberID;
END;
$$;


--
-- TOC entry 224 (class 1255 OID 58050)
-- Name: delete_memberupdate(integer); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.delete_memberupdate(IN memberid integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Set memberID to null for all transactions associated with the deleted member
    UPDATE Transactions SET memberID = null WHERE Transactions.memberID = delete_memberUpdate.memberid;

    -- Delete the member from the Member table
    DELETE FROM Member WHERE Member.memberID = delete_memberUpdate.memberID;
END;
$$;


--
-- TOC entry 225 (class 1255 OID 58051)
-- Name: get_association(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.get_association()
    LANGUAGE sql
    AS $$
    SELECT * FROM Association;
$$;


--
-- TOC entry 226 (class 1255 OID 58052)
-- Name: insert_into_association(character varying, character varying, character varying); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.insert_into_association(IN association_id character varying, IN association_name character varying, IN association_password character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO Association (accountID, name, password) VALUES (association_id, association_name, association_password);
END;
$$;


--
-- TOC entry 227 (class 1255 OID 58053)
-- Name: insert_into_file(character varying, character varying, character varying, real, real, character varying); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.insert_into_file(IN reference_number character varying, IN statement_number character varying, IN sequence_detail character varying, IN available_balance real, IN forward_avbalance real, IN account_id character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO File (referenceNumber, statementNumber, sequenceDetail, availableBalance,forwardAvBalance,accountID) VALUES (reference_Number, statement_Number, sequence_Detail, available_Balance,forward_AvBalance,account_ID);
END;
$$;


--
-- TOC entry 228 (class 1255 OID 58054)
-- Name: insert_into_member(character varying, character varying); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.insert_into_member(IN name character varying, IN email character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO Member (name, email) VALUES (name,email);
END;
$$;


--
-- TOC entry 229 (class 1255 OID 58055)
-- Name: insert_into_transaction(character varying, character varying, character varying, double precision, character varying, character varying, integer, integer, character varying); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.insert_into_transaction(IN referencenumber character varying, IN transactiondetail character varying, IN description character varying, IN amount double precision, IN currency character varying, IN transaction_date character varying, IN categoryid integer, IN memberid integer, IN typetransaction character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO Transactions (referenceNumber, transactionDetail, description, amount,currency,transaction_date,categoryID,memberID,typeTransaction) VALUES (referenceNumber, transactionDetail, description, amount,currency,transaction_date,categoryID,memberID,typeTransaction);
END;
$$;


--
-- TOC entry 230 (class 1255 OID 58056)
-- Name: search_table2(character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.search_table2(search_term character varying) RETURNS TABLE(transactionid integer, referencenumber character varying, transactiondetail character varying, description character varying, amount double precision, currency character varying, transaction_date character varying, categoryid integer, memberid integer, typetransaction character varying, member_id integer, name character varying, email character varying, category_id integer, na_me character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT *
               FROM select_join()
               WHERE select_join.name ILIKE ('%' || search_term || '%')
                     OR select_join.description ILIKE ('%' || search_term || '%')
					 OR select_join.na_me ILIKE ('%' || search_term || '%'); -- add additional columns as needed
END;
$$;


--
-- TOC entry 231 (class 1255 OID 58057)
-- Name: select_all_association(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_all_association() RETURNS TABLE(accountid character varying, name character varying, password character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT Association.accountID, Association.name, Association.password FROM Association;
END;
$$;


--
-- TOC entry 232 (class 1255 OID 58058)
-- Name: select_all_file(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_all_file() RETURNS TABLE(referencenumber character varying, statementnumber character varying, sequencedetail character varying, availablebalance real, forwardavbalance real, accountid character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT File.referenceNumber, File.statementNumber , File.sequenceDetail , File.availableBalance , File.forwardAvBalance , File.accountID  FROM File;
END;
$$;


--
-- TOC entry 233 (class 1255 OID 58059)
-- Name: select_all_member(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_all_member() RETURNS TABLE(memberid integer, name character varying, email character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT Member.memberID, Member.name, Member.email FROM Member;
END;
$$;


--
-- TOC entry 234 (class 1255 OID 58060)
-- Name: select_all_transaction(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_all_transaction() RETURNS TABLE(transactionid integer, referencenumber character varying, transactiondetail character varying, description character varying, amount double precision, currency character varying, transaction_date character varying, categoryid integer, memberid integer, typetransaction character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT Transactions.transactionID , Transactions.referenceNumber, Transactions.transactionDetail,
  						Transactions.description , Transactions.amount, Transactions.currency, Transactions.transaction_date, 
						Transactions.categoryID , Transactions.memberID , Transactions.typeTransaction   FROM Transactions;
END;
$$;


--
-- TOC entry 246 (class 1255 OID 58061)
-- Name: select_join(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_join() RETURNS TABLE(transactionid integer, referencenumber character varying, transactiondetail character varying, description character varying, amount double precision, currency character varying, transaction_date character varying, categoryid integer, memberid integer, typetransaction character varying, member_id integer, name character varying, email character varying, category_id integer, na_me character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY SELECT * 
FROM Transactions LEFT JOIN member
ON Transactions.memberID = Member.memberID
LEFT JOIN Category
ON Category.categoryID = Transactions.categoryID;
END;
$$;


--
-- TOC entry 247 (class 1255 OID 58062)
-- Name: select_member(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_member() RETURNS SETOF record
    LANGUAGE plpgsql
    AS $$
DECLARE
    rec record;
BEGIN
    FOR rec IN SELECT memberID, name, email FROM public.Member
    LOOP
        -- return each row of the result set
        RETURN NEXT rec;
    END LOOP;
END;
$$;


--
-- TOC entry 248 (class 1255 OID 58063)
-- Name: select_transaction_on_id(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.select_transaction_on_id(id integer) RETURNS TABLE(transactionid integer, referencenumber character varying, transactiondetail character varying, description character varying, amount double precision, currency character varying, transaction_date character varying, categoryid integer, memberid integer, typetransaction character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
  RETURN QUERY select * from transactions where transactions.transactionid = select_transaction_on_id.id;
END;
$$;


--
-- TOC entry 249 (class 1255 OID 58064)
-- Name: test_select(); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.test_select()
    LANGUAGE sql
    AS $_$CREATE OR REPLACE PROCEDURE add_new_member(
	new_part_name varchar,
	new_vendor_name varchar
) 
AS $$
DECLARE
	v_part_id INT;
	v_vendor_id INT;
BEGIN
	-- insert into the parts table
	INSERT INTO Member(name,email) 
	VALUES(new_part_name,new_vendor_name) 
	
END;
$$
LANGUAGE PLPGSQL;$_$;


--
-- TOC entry 250 (class 1255 OID 58065)
-- Name: update_transaction(integer, character varying, integer, integer); Type: PROCEDURE; Schema: public; Owner: -
--

CREATE PROCEDURE public.update_transaction(IN p_transactionid integer, IN p_description character varying, IN p_categoryid integer, IN p_memberid integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE Transactions
    SET 
        description = p_description,
        categoryID = p_categoryID,
        memberID = p_memberID
    WHERE 
        transactionID = p_transactionID;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 214 (class 1259 OID 58066)
-- Name: association; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.association (
    accountid character varying(35) NOT NULL,
    name character varying(50) NOT NULL,
    password character varying(256) NOT NULL
);


--
-- TOC entry 215 (class 1259 OID 58069)
-- Name: category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.category (
    categoryid integer NOT NULL,
    name character varying(32)
);


--
-- TOC entry 216 (class 1259 OID 58072)
-- Name: category_categoryid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.category_categoryid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3384 (class 0 OID 0)
-- Dependencies: 216
-- Name: category_categoryid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.category_categoryid_seq OWNED BY public.category.categoryid;


--
-- TOC entry 217 (class 1259 OID 58073)
-- Name: file; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.file (
    referencenumber character varying(16) NOT NULL,
    statementnumber character varying NOT NULL,
    sequencedetail character varying NOT NULL,
    availablebalance real NOT NULL,
    forwardavbalance real NOT NULL,
    accountid character varying(35) NOT NULL
);


--
-- TOC entry 218 (class 1259 OID 58078)
-- Name: full_join_view; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.full_join_view AS
 SELECT select_join.transactionid,
    select_join.referencenumber,
    select_join.transactiondetail,
    select_join.description,
    select_join.amount,
    select_join.currency,
    select_join.transaction_date,
    select_join.categoryid,
    select_join.memberid,
    select_join.typetransaction,
    select_join.member_id,
    select_join.name,
    select_join.email,
    select_join.category_id,
    select_join.na_me
   FROM public.select_join() select_join(transactionid, referencenumber, transactiondetail, description, amount, currency, transaction_date, categoryid, memberid, typetransaction, member_id, name, email, category_id, na_me);


--
-- TOC entry 219 (class 1259 OID 58082)
-- Name: member; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.member (
    memberid integer NOT NULL,
    name character varying(32) NOT NULL,
    email character varying(254) NOT NULL
);


--
-- TOC entry 220 (class 1259 OID 58085)
-- Name: member_memberid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.member_memberid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3385 (class 0 OID 0)
-- Dependencies: 220
-- Name: member_memberid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.member_memberid_seq OWNED BY public.member.memberid;


--
-- TOC entry 221 (class 1259 OID 58086)
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    transactionid integer NOT NULL,
    referencenumber character varying(16),
    transactiondetail character varying,
    description character varying(128),
    amount double precision NOT NULL,
    currency character varying(3) NOT NULL,
    transaction_date character varying(10),
    categoryid integer,
    memberid integer,
    typetransaction character varying
);


--
-- TOC entry 222 (class 1259 OID 58091)
-- Name: transactions_transactionid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.transactions_transactionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3386 (class 0 OID 0)
-- Dependencies: 222
-- Name: transactions_transactionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.transactions_transactionid_seq OWNED BY public.transactions.transactionid;


--
-- TOC entry 3212 (class 2604 OID 58092)
-- Name: category categoryid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category ALTER COLUMN categoryid SET DEFAULT nextval('public.category_categoryid_seq'::regclass);


--
-- TOC entry 3213 (class 2604 OID 58093)
-- Name: member memberid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.member ALTER COLUMN memberid SET DEFAULT nextval('public.member_memberid_seq'::regclass);


--
-- TOC entry 3214 (class 2604 OID 58094)
-- Name: transactions transactionid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions ALTER COLUMN transactionid SET DEFAULT nextval('public.transactions_transactionid_seq'::regclass);


--
-- TOC entry 3371 (class 0 OID 58066)
-- Dependencies: 214
-- Data for Name: association; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.association (accountid, name, password) FROM stdin;
\.


--
-- TOC entry 3372 (class 0 OID 58069)
-- Dependencies: 215
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.category (categoryid, name) FROM stdin;
2	Bar
\.


--
-- TOC entry 3374 (class 0 OID 58073)
-- Dependencies: 217
-- Data for Name: file; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.file (referencenumber, statementnumber, sequencedetail, availablebalance, forwardavbalance, accountid) FROM stdin;
\.


--
-- TOC entry 3375 (class 0 OID 58082)
-- Dependencies: 219
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.member (memberid, name, email) FROM stdin;
10	TestName	new@gmail.com
\.


--
-- TOC entry 3377 (class 0 OID 58086)
-- Dependencies: 221
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transactions (transactionid, referencenumber, transactiondetail, description, amount, currency, transaction_date, categoryid, memberid, typetransaction) FROM stdin;
\.


--
-- TOC entry 3387 (class 0 OID 0)
-- Dependencies: 216
-- Name: category_categoryid_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.category_categoryid_seq', 2, true);


--
-- TOC entry 3388 (class 0 OID 0)
-- Dependencies: 220
-- Name: member_memberid_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.member_memberid_seq', 18, true);


--
-- TOC entry 3389 (class 0 OID 0)
-- Dependencies: 222
-- Name: transactions_transactionid_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transactions_transactionid_seq', 220, true);


--
-- TOC entry 3216 (class 2606 OID 58096)
-- Name: association association_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.association
    ADD CONSTRAINT association_pkey PRIMARY KEY (accountid);


--
-- TOC entry 3218 (class 2606 OID 58098)
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (categoryid);


--
-- TOC entry 3220 (class 2606 OID 58100)
-- Name: file file_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.file
    ADD CONSTRAINT file_pkey PRIMARY KEY (referencenumber);


--
-- TOC entry 3222 (class 2606 OID 58102)
-- Name: member member_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (memberid);


--
-- TOC entry 3224 (class 2606 OID 58104)
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (transactionid);


--
-- TOC entry 3225 (class 2606 OID 58105)
-- Name: transactions transactions_categoryid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_categoryid_fkey FOREIGN KEY (categoryid) REFERENCES public.category(categoryid) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 3226 (class 2606 OID 58110)
-- Name: transactions transactions_memberid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_memberid_fkey FOREIGN KEY (memberid) REFERENCES public.member(memberid) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 3227 (class 2606 OID 58115)
-- Name: transactions transactions_referencenumber_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_referencenumber_fkey FOREIGN KEY (referencenumber) REFERENCES public.file(referencenumber) ON DELETE CASCADE;


-- Completed on 2023-10-04 11:59:04

--
-- PostgreSQL database dump complete
--

