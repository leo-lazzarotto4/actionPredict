# Étape 1: Construire l'application
FROM node:16 AS build

# Définir le répertoire de travail
WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier tout le reste du code dans le conteneur
COPY . .

# Construire l'application pour la production
RUN npm run build

# Étape 2: Servir l'application
FROM nginx:alpine

# Copier les fichiers de build vers le dossier par défaut de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Exposer le port sur lequel Nginx écoute (par défaut 80)
EXPOSE 80

# Démarrer Nginx en mode non-bloquant
CMD ["nginx", "-g", "daemon off;"]
