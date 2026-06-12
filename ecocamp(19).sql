-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Hôte : ecocamp_mariadb
-- Généré le : ven. 12 juin 2026 à 08:34
-- Version du serveur : 12.3.2-MariaDB-ubu2404
-- Version de PHP : 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `ecocamp`
--

-- --------------------------------------------------------

--
-- Structure de la table `administrateur`
--

CREATE TABLE `administrateur` (
  `id_administrateur` bigint(20) NOT NULL,
  `login_administrateur` varchar(50) NOT NULL,
  `mdp_administrateur` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `administrateur`
--

INSERT INTO `administrateur` (`id_administrateur`, `login_administrateur`, `mdp_administrateur`) VALUES
(1, 'admin_ecocamp', '$2b$12$R8bs5jxZyw9qs.hRdKymmOpWYTY62L.qNsfDh9br8EHaI6UQYKwFC');

-- --------------------------------------------------------

--
-- Structure de la table `compteur`
--

CREATE TABLE `compteur` (
  `id_compteur` bigint(20) NOT NULL,
  `index_compteur` float NOT NULL,
  `reference_compteur` varchar(50) NOT NULL,
  `id_hebergement` bigint(20) NOT NULL,
  `id_type_flux` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `consommation`
--

CREATE TABLE `consommation` (
  `id_consommation` bigint(20) NOT NULL,
  `index_consommation` float DEFAULT NULL,
  `id_type_flux` bigint(20) NOT NULL,
  `id_hebergement` bigint(20) NOT NULL,
  `date_consommation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `consommation`
--

INSERT INTO `consommation` (`id_consommation`, `index_consommation`, `id_type_flux`, `id_hebergement`, `date_consommation`) VALUES
(81, 0, 3, 2, '2026-04-22 09:00:00'),
(82, 0, 4, 2, '2026-04-22 09:00:00'),
(83, 12.5, 3, 2, '2026-04-23 09:00:00'),
(84, 0.38, 4, 2, '2026-04-23 09:00:00'),
(85, 25.1, 3, 2, '2026-04-24 09:00:00'),
(86, 0.77, 4, 2, '2026-04-24 09:00:00'),
(87, 37.8, 3, 2, '2026-04-25 09:00:00'),
(88, 1.16, 4, 2, '2026-04-25 09:00:00'),
(89, 50.4, 3, 2, '2026-04-26 09:00:00'),
(90, 1.56, 4, 2, '2026-04-26 09:00:00'),
(91, 63.1, 3, 2, '2026-04-27 09:00:00'),
(92, 1.96, 4, 2, '2026-04-27 09:00:00'),
(93, 75.9, 3, 2, '2026-04-28 09:00:00'),
(94, 2.37, 4, 2, '2026-04-28 09:00:00'),
(95, 88.6, 3, 2, '2026-04-29 09:00:00'),
(96, 2.78, 4, 2, '2026-04-29 09:00:00'),
(97, 101.4, 3, 2, '2026-04-30 09:00:00'),
(98, 3.19, 4, 2, '2026-04-30 09:00:00'),
(99, 114.2, 3, 2, '2026-05-01 09:00:00'),
(100, 3.61, 4, 2, '2026-05-01 09:00:00'),
(101, 127, 3, 2, '2026-05-02 09:00:00'),
(102, 4.03, 4, 2, '2026-05-02 09:00:00'),
(103, 139.8, 3, 2, '2026-05-03 09:00:00'),
(104, 4.46, 4, 2, '2026-05-03 09:00:00'),
(105, 152.7, 3, 2, '2026-05-04 09:00:00'),
(106, 4.89, 4, 2, '2026-05-04 09:00:00'),
(107, 165.6, 3, 2, '2026-05-05 09:00:00'),
(108, 5.33, 4, 2, '2026-05-05 09:00:00'),
(109, 178.5, 3, 2, '2026-05-06 09:00:00'),
(110, 5.77, 4, 2, '2026-05-06 09:00:00'),
(111, 191.5, 3, 2, '2026-05-07 09:00:00'),
(112, 6.22, 4, 2, '2026-05-07 09:00:00'),
(113, 204.5, 3, 2, '2026-05-08 09:00:00'),
(114, 6.67, 4, 2, '2026-05-08 09:00:00'),
(115, 217.5, 3, 2, '2026-05-09 09:00:00'),
(116, 7.13, 4, 2, '2026-05-09 09:00:00'),
(117, 230.6, 3, 2, '2026-05-10 09:00:00'),
(118, 7.59, 4, 2, '2026-05-10 09:00:00'),
(119, 243.8, 3, 2, '2026-05-11 09:00:00'),
(120, 8.06, 4, 2, '2026-05-11 09:00:00'),
(121, 257, 3, 2, '2026-05-12 09:00:00'),
(122, 8.53, 4, 2, '2026-05-12 09:00:00'),
(123, 270.2, 3, 2, '2026-05-13 09:00:00'),
(124, 9.01, 4, 2, '2026-05-13 09:00:00'),
(125, 283.5, 3, 2, '2026-05-14 09:00:00'),
(126, 9.49, 4, 2, '2026-05-14 09:00:00'),
(127, 296.9, 3, 2, '2026-05-15 09:00:00'),
(128, 9.98, 4, 2, '2026-05-15 09:00:00'),
(129, 310.3, 3, 2, '2026-05-16 09:00:00'),
(130, 10.47, 4, 2, '2026-05-16 09:00:00'),
(131, 323.7, 3, 2, '2026-05-17 09:00:00'),
(132, 10.97, 4, 2, '2026-05-17 09:00:00'),
(133, 337.2, 3, 2, '2026-05-18 09:00:00'),
(134, 11.47, 4, 2, '2026-05-18 09:00:00'),
(135, 350.7, 3, 2, '2026-05-19 09:00:00'),
(136, 11.98, 4, 2, '2026-05-19 09:00:00'),
(137, 364.3, 3, 2, '2026-05-20 09:00:00'),
(138, 12.49, 4, 2, '2026-05-20 09:00:00'),
(139, 377.9, 3, 2, '2026-05-21 09:00:00'),
(140, 13.01, 4, 2, '2026-05-21 09:00:00'),
(141, 391.6, 3, 2, '2026-05-22 09:00:00'),
(142, 13.53, 4, 2, '2026-05-22 09:00:00'),
(143, 405.3, 3, 2, '2026-05-23 09:00:00'),
(144, 14.06, 4, 2, '2026-05-23 09:00:00'),
(145, 419.1, 3, 2, '2026-05-24 09:00:00'),
(146, 14.59, 4, 2, '2026-05-24 09:00:00'),
(147, 432.9, 3, 2, '2026-05-25 09:00:00'),
(148, 15.13, 4, 2, '2026-05-25 09:00:00'),
(149, 446.8, 3, 2, '2026-05-26 09:00:00'),
(150, 15.67, 4, 2, '2026-05-26 09:00:00'),
(151, 460.7, 3, 2, '2026-05-27 09:00:00'),
(152, 16.22, 4, 2, '2026-05-27 09:00:00'),
(153, 474.7, 3, 2, '2026-05-28 09:00:00'),
(154, 16.77, 4, 2, '2026-05-28 09:00:00'),
(155, 488.7, 3, 2, '2026-05-29 09:00:00'),
(156, 17.33, 4, 2, '2026-05-29 09:00:00'),
(157, 502.8, 3, 2, '2026-05-30 09:00:00'),
(158, 17.89, 4, 2, '2026-05-30 09:00:00'),
(159, 516.9, 3, 2, '2026-05-31 09:00:00'),
(160, 18.46, 4, 2, '2026-05-31 09:00:00'),
(161, 30, 4, 7, '2026-06-02 09:16:14'),
(162, 30, 4, 7, '2026-06-02 09:17:46'),
(163, 30, 4, 7, '2026-06-02 09:18:46'),
(164, 30, 4, 7, '2026-06-02 09:19:46'),
(166, 30, 4, 7, '2026-06-02 09:20:46'),
(168, 30, 4, 7, '2026-06-02 09:21:46'),
(170, 30, 4, 7, '2026-06-02 09:22:46'),
(172, 30, 4, 7, '2026-06-02 09:23:46'),
(174, 30, 4, 7, '2026-06-02 09:28:46'),
(175, 158, 3, 7, '2026-06-02 09:28:46'),
(176, 31, 4, 7, '2026-06-03 09:00:00'),
(177, 32, 4, 7, '2026-06-04 09:00:00'),
(178, 33, 4, 7, '2026-06-05 09:00:00'),
(179, 34, 4, 7, '2026-06-06 09:00:00'),
(180, 35, 4, 7, '2026-06-07 09:00:00'),
(181, 36, 4, 7, '2026-06-08 09:00:00'),
(182, 37, 4, 7, '2026-06-09 09:00:00'),
(183, 38, 4, 7, '2026-06-10 09:00:00'),
(184, 39, 4, 7, '2026-06-11 09:00:00'),
(185, 40, 4, 7, '2026-06-12 09:00:00'),
(186, 41, 4, 7, '2026-06-13 09:00:00'),
(187, 42, 4, 7, '2026-06-14 09:00:00'),
(188, 43, 4, 7, '2026-06-15 09:00:00'),
(189, 44, 4, 7, '2026-06-16 09:00:00'),
(190, 45, 4, 7, '2026-06-17 09:00:00'),
(191, 46, 4, 7, '2026-06-18 09:00:00'),
(192, 47, 4, 7, '2026-06-19 09:00:00'),
(193, 48, 4, 7, '2026-06-20 09:00:00'),
(194, 160, 3, 7, '2026-06-03 09:00:00'),
(195, 162, 3, 7, '2026-06-04 09:00:00'),
(196, 164, 3, 7, '2026-06-05 09:00:00'),
(197, 166, 3, 7, '2026-06-06 09:00:00'),
(198, 168, 3, 7, '2026-06-07 09:00:00'),
(199, 170, 3, 7, '2026-06-08 09:00:00'),
(200, 172, 3, 7, '2026-06-09 09:00:00'),
(201, 174, 3, 7, '2026-06-10 09:00:00'),
(202, 176, 3, 7, '2026-06-11 09:00:00'),
(203, 178, 3, 7, '2026-06-12 09:00:00'),
(204, 180, 3, 7, '2026-06-13 09:00:00'),
(205, 182, 3, 7, '2026-06-14 09:00:00'),
(206, 184, 3, 7, '2026-06-15 09:00:00'),
(207, 186, 3, 7, '2026-06-16 09:00:00'),
(208, 188, 3, 7, '2026-06-17 09:00:00'),
(209, 190, 3, 7, '2026-06-18 09:00:00'),
(210, 192, 3, 7, '2026-06-19 09:00:00'),
(211, 194, 3, 7, '2026-06-20 09:00:00'),
(222, 12, 4, 1, '2026-06-06 09:00:00'),
(223, 14, 4, 1, '2026-06-07 09:00:00'),
(224, 17, 4, 1, '2026-06-08 09:00:00'),
(225, 19, 4, 1, '2026-06-09 09:00:00'),
(226, 22, 4, 1, '2026-06-10 09:00:00'),
(227, 25, 4, 1, '2026-06-11 09:00:00'),
(228, 28, 4, 1, '2026-06-12 09:00:00'),
(229, 324, 3, 1, '2026-06-06 09:00:00'),
(230, 327, 3, 1, '2026-06-07 09:00:00'),
(231, 330, 3, 1, '2026-06-08 09:00:00'),
(232, 334, 3, 1, '2026-06-09 09:00:00'),
(233, 338, 3, 1, '2026-06-10 09:00:00'),
(234, 342, 3, 1, '2026-06-11 09:00:00'),
(235, 347, 3, 1, '2026-06-12 09:00:00'),
(236, 26887.2, 3, 1, '2026-06-12 08:33:41'),
(237, 26887.2, 3, 1, '2026-06-12 08:33:49');

-- --------------------------------------------------------

--
-- Structure de la table `hebergement`
--

CREATE TABLE `hebergement` (
  `id_hebergement` bigint(20) NOT NULL,
  `nom_hebergement` varchar(100) NOT NULL,
  `id_type_logement` int(11) DEFAULT NULL,
  `adresse_mac` varchar(17) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `hebergement`
--

INSERT INTO `hebergement` (`id_hebergement`, `nom_hebergement`, `id_type_logement`, `adresse_mac`) VALUES
(1, 'Mobil-home_01', 1, '88:a2:9e:9a:25:63'),
(2, 'Mobil-home_02', 2, '88:a2:9e:9a:24:c4'),
(7, 'Mobil-home_03', 3, '88:a2:9e:9a:25:65'),
(8, 'Mobil-home_04', 1, '88:a2:9e:9a:25:66'),
(9, 'Mobil-home_05', 2, '88:a2:9e:9a:25:67'),
(10, 'Mobil-home_06', 3, '88:a2:9e:9a:25:68');

-- --------------------------------------------------------

--
-- Structure de la table `historique_consommation`
--

CREATE TABLE `historique_consommation` (
  `id_historique_consommation` bigint(20) NOT NULL,
  `date_mesure_historique` datetime DEFAULT NULL,
  `eau_historique_consommation` float DEFAULT NULL,
  `electricite_historique_consommation` float DEFAULT NULL,
  `id_sejour` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `historique_consommation`
--

INSERT INTO `historique_consommation` (`id_historique_consommation`, `date_mesure_historique`, `eau_historique_consommation`, `electricite_historique_consommation`, `id_sejour`) VALUES
(46, '2026-06-06 00:00:00', 11.68, 322.6, 42);

-- --------------------------------------------------------

--
-- Structure de la table `message`
--

CREATE TABLE `message` (
  `id_message` bigint(20) NOT NULL,
  `contenu_message` varchar(255) DEFAULT NULL,
  `date_debut_message` date DEFAULT NULL,
  `date_fin_message` date DEFAULT NULL,
  `horaire_evenement_message` time DEFAULT NULL,
  `id_type_message` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `message`
--

INSERT INTO `message` (`id_message`, `contenu_message`, `date_debut_message`, `date_fin_message`, `horaire_evenement_message`, `id_type_message`) VALUES
(57, 'piscine fermée', '2026-06-11', '2026-06-14', NULL, 2),
(58, 'Soirée grillade', '2026-06-11', '2026-06-11', '22:00:00', 1);

-- --------------------------------------------------------

--
-- Structure de la table `quota`
--

CREATE TABLE `quota` (
  `id_quota` bigint(20) NOT NULL,
  `eau_quota` float DEFAULT NULL,
  `electicite_quota` float DEFAULT NULL,
  `id_sejour` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `sejour`
--

CREATE TABLE `sejour` (
  `id_sejour` bigint(20) NOT NULL,
  `date_debut_sejour` datetime DEFAULT NULL,
  `date_fin_sejour` datetime DEFAULT NULL,
  `id_hebergement` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `sejour`
--

INSERT INTO `sejour` (`id_sejour`, `date_debut_sejour`, `date_fin_sejour`, `id_hebergement`) VALUES
(42, '2026-06-06 00:00:00', '2026-06-14 00:00:00', 1);

-- --------------------------------------------------------

--
-- Structure de la table `tableau_de_bord`
--

CREATE TABLE `tableau_de_bord` (
  `id_tableau` bigint(20) NOT NULL,
  `reference_tableau` varchar(255) NOT NULL,
  `id_hebergement` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `type_flux`
--

CREATE TABLE `type_flux` (
  `id_type_flux` bigint(20) NOT NULL,
  `nom_type_flux` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `type_flux`
--

INSERT INTO `type_flux` (`id_type_flux`, `nom_type_flux`) VALUES
(4, 'Eau'),
(3, 'Électricité');

-- --------------------------------------------------------

--
-- Structure de la table `type_logement`
--

CREATE TABLE `type_logement` (
  `id_type_logement` int(11) NOT NULL,
  `nom_type` varchar(50) NOT NULL,
  `quota_eau_max` float NOT NULL,
  `quota_elec_max` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Déchargement des données de la table `type_logement`
--

INSERT INTO `type_logement` (`id_type_logement`, `nom_type`, `quota_eau_max`, `quota_elec_max`) VALUES
(1, 'Standard (2-4 pers)', 12, 25),
(2, 'Confort (6 pers)', 50, 25),
(3, 'Luxe (8 pers)', 0.65, 35);

-- --------------------------------------------------------

--
-- Structure de la table `type_message`
--

CREATE TABLE `type_message` (
  `id_type_message` bigint(20) NOT NULL,
  `nom_type_message` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `type_message`
--

INSERT INTO `type_message` (`id_type_message`, `nom_type_message`) VALUES
(3, 'Alerte Consommation'),
(1, 'Evenement'),
(2, 'Messages');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `administrateur`
--
ALTER TABLE `administrateur`
  ADD PRIMARY KEY (`id_administrateur`),
  ADD UNIQUE KEY `login_administrateur` (`login_administrateur`),
  ADD UNIQUE KEY `mdp_administrateur` (`mdp_administrateur`);

--
-- Index pour la table `compteur`
--
ALTER TABLE `compteur`
  ADD PRIMARY KEY (`id_compteur`),
  ADD UNIQUE KEY `index_compteur` (`index_compteur`),
  ADD UNIQUE KEY `reference_compteur` (`reference_compteur`),
  ADD KEY `FK_Compteur_id_hebergement` (`id_hebergement`),
  ADD KEY `FK_Compteur_id_type_flux` (`id_type_flux`);

--
-- Index pour la table `consommation`
--
ALTER TABLE `consommation`
  ADD PRIMARY KEY (`id_consommation`),
  ADD KEY `FK_Consommation_id_type_flux` (`id_type_flux`),
  ADD KEY `FK_Consommation_id_hebergement` (`id_hebergement`);

--
-- Index pour la table `hebergement`
--
ALTER TABLE `hebergement`
  ADD PRIMARY KEY (`id_hebergement`),
  ADD UNIQUE KEY `nom_hebergement` (`nom_hebergement`),
  ADD KEY `fk_type_logement` (`id_type_logement`);

--
-- Index pour la table `historique_consommation`
--
ALTER TABLE `historique_consommation`
  ADD PRIMARY KEY (`id_historique_consommation`),
  ADD KEY `FK_Historique_cosommation_id_sejour` (`id_sejour`);

--
-- Index pour la table `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id_message`),
  ADD KEY `FK_Message_id_type_message` (`id_type_message`);

--
-- Index pour la table `quota`
--
ALTER TABLE `quota`
  ADD PRIMARY KEY (`id_quota`),
  ADD KEY `FK_Quota_id_sejour` (`id_sejour`);

--
-- Index pour la table `sejour`
--
ALTER TABLE `sejour`
  ADD PRIMARY KEY (`id_sejour`),
  ADD KEY `FK_Sejour_id_hebergement` (`id_hebergement`);

--
-- Index pour la table `tableau_de_bord`
--
ALTER TABLE `tableau_de_bord`
  ADD PRIMARY KEY (`id_tableau`),
  ADD UNIQUE KEY `reference_tableau` (`reference_tableau`),
  ADD KEY `FK_Tableau_de_bord_id_hebergement` (`id_hebergement`);

--
-- Index pour la table `type_flux`
--
ALTER TABLE `type_flux`
  ADD PRIMARY KEY (`id_type_flux`),
  ADD UNIQUE KEY `nom_type_flux` (`nom_type_flux`);

--
-- Index pour la table `type_logement`
--
ALTER TABLE `type_logement`
  ADD PRIMARY KEY (`id_type_logement`);

--
-- Index pour la table `type_message`
--
ALTER TABLE `type_message`
  ADD PRIMARY KEY (`id_type_message`),
  ADD UNIQUE KEY `nom_type_message` (`nom_type_message`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `administrateur`
--
ALTER TABLE `administrateur`
  MODIFY `id_administrateur` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `compteur`
--
ALTER TABLE `compteur`
  MODIFY `id_compteur` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `consommation`
--
ALTER TABLE `consommation`
  MODIFY `id_consommation` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=238;

--
-- AUTO_INCREMENT pour la table `hebergement`
--
ALTER TABLE `hebergement`
  MODIFY `id_hebergement` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `historique_consommation`
--
ALTER TABLE `historique_consommation`
  MODIFY `id_historique_consommation` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT pour la table `message`
--
ALTER TABLE `message`
  MODIFY `id_message` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;

--
-- AUTO_INCREMENT pour la table `quota`
--
ALTER TABLE `quota`
  MODIFY `id_quota` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `sejour`
--
ALTER TABLE `sejour`
  MODIFY `id_sejour` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT pour la table `tableau_de_bord`
--
ALTER TABLE `tableau_de_bord`
  MODIFY `id_tableau` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `type_flux`
--
ALTER TABLE `type_flux`
  MODIFY `id_type_flux` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `type_logement`
--
ALTER TABLE `type_logement`
  MODIFY `id_type_logement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `type_message`
--
ALTER TABLE `type_message`
  MODIFY `id_type_message` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `compteur`
--
ALTER TABLE `compteur`
  ADD CONSTRAINT `FK_Compteur_id_hebergement` FOREIGN KEY (`id_hebergement`) REFERENCES `hebergement` (`id_hebergement`),
  ADD CONSTRAINT `FK_Compteur_id_type_flux` FOREIGN KEY (`id_type_flux`) REFERENCES `type_flux` (`id_type_flux`);

--
-- Contraintes pour la table `consommation`
--
ALTER TABLE `consommation`
  ADD CONSTRAINT `FK_Consommation_id_hebergement` FOREIGN KEY (`id_hebergement`) REFERENCES `hebergement` (`id_hebergement`),
  ADD CONSTRAINT `FK_Consommation_id_type_flux` FOREIGN KEY (`id_type_flux`) REFERENCES `type_flux` (`id_type_flux`);

--
-- Contraintes pour la table `hebergement`
--
ALTER TABLE `hebergement`
  ADD CONSTRAINT `fk_type_logement` FOREIGN KEY (`id_type_logement`) REFERENCES `type_logement` (`id_type_logement`);

--
-- Contraintes pour la table `historique_consommation`
--
ALTER TABLE `historique_consommation`
  ADD CONSTRAINT `FK_Historique_cosommation_id_sejour` FOREIGN KEY (`id_sejour`) REFERENCES `sejour` (`id_sejour`);

--
-- Contraintes pour la table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `FK_Message_id_type_message` FOREIGN KEY (`id_type_message`) REFERENCES `type_message` (`id_type_message`);

--
-- Contraintes pour la table `quota`
--
ALTER TABLE `quota`
  ADD CONSTRAINT `FK_Quota_id_sejour` FOREIGN KEY (`id_sejour`) REFERENCES `sejour` (`id_sejour`);

--
-- Contraintes pour la table `sejour`
--
ALTER TABLE `sejour`
  ADD CONSTRAINT `FK_Sejour_id_hebergement` FOREIGN KEY (`id_hebergement`) REFERENCES `hebergement` (`id_hebergement`);

--
-- Contraintes pour la table `tableau_de_bord`
--
ALTER TABLE `tableau_de_bord`
  ADD CONSTRAINT `FK_Tableau_de_bord_id_hebergement` FOREIGN KEY (`id_hebergement`) REFERENCES `hebergement` (`id_hebergement`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
