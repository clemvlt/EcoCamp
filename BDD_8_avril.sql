-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Hôte : ecocamp_mariadb
-- Généré le : mer. 08 avr. 2026 à 14:14
-- Version du serveur : 12.2.2-MariaDB-ubu2404
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
(1, 'admin_ecocamp', '$2b$12$kfBGiDO3f194qLtlZPB0qOyfFTp9QHASqkCB1YlLXl6Pd9NQ5frO6');

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
(252, 240, 4, 1, '2026-03-31 10:00:00'),
(254, 150, 3, 1, '2026-03-30 09:52:16'),
(255, 265, 4, 1, '2026-04-02 14:07:57'),
(256, 150, 3, 1, '2026-04-02 14:07:57'),
(258, 240, 4, 1, '2026-04-03 14:29:54'),
(259, 220, 3, 1, '2026-04-03 14:29:54'),
(260, 295, 4, 1, '2026-04-04 14:29:54'),
(261, 180.8, 3, 1, '2026-04-04 14:29:54'),
(262, 312.3, 4, 1, '2026-04-05 14:29:54'),
(263, 198.5, 3, 1, '2026-04-05 14:29:54'),
(264, 330.1, 4, 1, '2026-04-06 14:29:54'),
(265, 215, 3, 1, '2026-04-06 14:29:54'),
(266, 355.8, 4, 1, '2026-04-07 14:29:54'),
(267, 240.4, 3, 1, '2026-04-07 14:29:54'),
(268, 100, 3, 2, '2026-04-01 14:00:00'),
(269, 112.5, 3, 2, '2026-04-02 14:00:00'),
(270, 128.2, 3, 2, '2026-04-03 14:00:00'),
(271, 145, 3, 2, '2026-04-04 14:00:00'),
(272, 160.3, 3, 2, '2026-04-05 14:00:00'),
(273, 178.9, 3, 2, '2026-04-06 14:00:00'),
(274, 195.4, 3, 2, '2026-04-07 14:00:00'),
(275, 200, 4, 2, '2026-04-01 14:05:00'),
(276, 245, 4, 2, '2026-04-02 14:05:00'),
(277, 290, 4, 2, '2026-04-03 14:05:00'),
(278, 350, 4, 2, '2026-04-04 14:05:00'),
(279, 410, 4, 2, '2026-04-05 14:05:00'),
(280, 465, 4, 2, '2026-04-06 14:05:00'),
(281, 520, 4, 2, '2026-04-07 14:05:00');

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
(1, 'Mobil-home  01', 1, '88:a2:9e:9a:25:63'),
(2, 'Mobil-home  02', 2, '88:a2:9e:9a:24:c4'),
(7, 'Mobil-home  03', 3, '88:a2:9e:9a:25:65'),
(8, 'Mobil-home  04', 1, '88:a2:9e:9a:25:66'),
(9, 'Mobil-home  05', 2, '88:a2:9e:9a:25:67'),
(10, 'Mobil-home  06', 3, '88:a2:9e:9a:25:68');

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
(28, '2026-03-24 09:00:00', 0, 0, 29),
(29, '2026-03-25 09:00:00', 0, 0, 29),
(30, '2026-03-26 09:00:00', 0, 0, 29),
(31, '2026-03-27 09:00:00', 0, 0, 29),
(32, '2026-03-28 09:00:00', 0, 0, 29),
(33, '2026-03-29 09:00:00', 0, 0, 29),
(34, '2026-03-30 09:00:00', 0, 0, 29);

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
(2, 'Pensez à éteindre les lumières en sortant !', '2026-06-01', '2026-08-31', NULL, 2);

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
(29, '2026-03-30 00:00:00', '2026-04-10 00:00:00', 1),
(30, '2026-03-30 00:00:00', '2026-04-05 00:00:00', 2);

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
(1, 'Standard (2-4 pers)', 50, 50),
(2, 'Confort (6 pers)', 200, 200),
(3, 'Luxe (8 pers)', 800, 500);

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
(5, 'Événement Camping'),
(4, 'Information Éco-geste'),
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
  MODIFY `id_consommation` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=282;

--
-- AUTO_INCREMENT pour la table `hebergement`
--
ALTER TABLE `hebergement`
  MODIFY `id_hebergement` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `historique_consommation`
--
ALTER TABLE `historique_consommation`
  MODIFY `id_historique_consommation` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT pour la table `message`
--
ALTER TABLE `message`
  MODIFY `id_message` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `quota`
--
ALTER TABLE `quota`
  MODIFY `id_quota` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `sejour`
--
ALTER TABLE `sejour`
  MODIFY `id_sejour` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

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
