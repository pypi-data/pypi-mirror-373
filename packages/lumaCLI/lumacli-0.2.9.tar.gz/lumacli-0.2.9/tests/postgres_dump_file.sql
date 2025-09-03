-- PostgreSQL database dump

-- Dumped from database version 14.8 (Ubuntu 14.8-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.8 (Ubuntu 14.8-0ubuntu0.22.04.1)

-- Started on 2023-07-03 12:19:34 WEST

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 214 (class 1259 OID 16412)
-- Name: orders; Type: TABLE; Schema: public; Owner: john_doe
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id integer,
    product_id integer,
    quantity integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.orders OWNER TO john_doe;

--
-- TOC entry 213 (class 1259 OID 16411)
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: john_doe
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO john_doe;

--
-- TOC entry 3375 (class 0 OID 0)
-- Dependencies: 213
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: john_doe
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- TOC entry 210 (class 1259 OID 16387)
-- Name: products; Type: TABLE; Schema: public; Owner: john_doe
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(100),
    price numeric(10,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.products OWNER TO john_doe;

--
-- TOC entry 209 (class 1259 OID 16386)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: john_doe
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO john_doe;

--
-- TOC entry 3376 (class 0 OID 0)
-- Dependencies: 209
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: john_doe
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 212 (class 1259 OID 16403)
-- Name: users; Type: TABLE; Schema: public; Owner: john_doe
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(50),
    email character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO john_doe;

--
-- TOC entry 211 (class 1259 OID 16402)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: john_doe
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO john_doe;

--
-- TOC entry 3377 (class 0 OID 0)
-- Dependencies: 211
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: john_doe
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3221 (class 2604 OID 16415)
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- TOC entry 3217 (class 2604 OID 16390)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 3219 (class 2604 OID 16406)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3228 (class 2606 OID 16418)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 3224 (class 2606 OID 16393)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 3226 (class 2606 OID 16409)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3230 (class 2606 OID 16424)
-- Name: orders orders_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 3229 (class 2606 OID 16419)
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: john_doe
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


-- Completed on 2023-07-03 12:19:34 WEST

-- PostgreSQL database dump complete
